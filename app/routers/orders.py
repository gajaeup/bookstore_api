from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem, Book, User, OrderStatus, UserRole
from app.schemas import APIResponse, OrderCreate, OrderDto, OrderItemDto, OrderUpdate
from app.dependencies import get_current_user
from app.exceptions import CustomException
from app.error_codes import ErrorCode
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pydantic import Field
class ErrorResponse(BaseModel):
    timestamp: str = Field(..., example="2025-12-14T12:00:00Z")
    path: str = Field(..., example="/api/request/url")
    status: int = Field(..., example=400)
    code: str = Field(..., example="ERROR_CODE_EXAMPLE")
    message: str = Field(..., example="에러 메시지가 여기에 나옵니다.")
    details: Optional[Dict[str, Any]] = Field(None, example={"field": "error_detail"})
common_responses = {
    400: {"model": ErrorResponse, "description": "잘못된 요청"},
    401: {"model": ErrorResponse, "description": "인증 실패"},
    403: {"model": ErrorResponse, "description": "권한 없음"},
    404: {"model": ErrorResponse, "description": "찾을 수 없음"},
    500: {"model": ErrorResponse, "description": "서버 오류"},
}
router = APIRouter(responses=common_responses)

# 1. 주문 생성
@router.post("/api/orders", response_model=APIResponse)
def create_order(
    order_req: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not order_req.items:
        return APIResponse(isSuccess=False, message="주문할 상품이 없습니다.")

    total_amount = 0
    order_items_data = []

    # 1. 가격 계산 및 유효성 검사
    for item in order_req.items:
        book = db.query(Book).filter(Book.book_id == item.book_id).first()
        if not book:
            return APIResponse(isSuccess=False, message=f"도서(ID: {item.book_id})를 찾을 수 없습니다.")
        if item.quantity > 100: 
            raise CustomException(ErrorCode.OUT_OF_STOCK)
        # 가격 합산
        price = float(book.price)
        total_amount += price * item.quantity
        
        # 나중에 저장하기 위해 데이터 모으기
        order_items_data.append({
            "book_id": item.book_id,
            "quantity": item.quantity,
            "price": price
        })
        

    # 2. 주문 정보 저장 (Order)
    new_order = Order(
        user_id=current_user.user_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING # 기본 상태: 결제 대기
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # 3. 주문 상세 저장 (OrderItem)
    for item_data in order_items_data:
        new_item = OrderItem(
            order_id=new_order.order_id,
            book_id=item_data["book_id"],
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(new_item)
    
    db.commit()

    return APIResponse(
        isSuccess=True, 
        message="주문이 완료되었습니다.", 
        payload={"order_id": new_order.order_id, "total_amount": total_amount}
    )

# 2. 내 주문 목록 조회
@router.get("/api/orders", response_model=APIResponse[list[OrderDto]])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 최신순 조회
    orders = db.query(Order).filter(Order.user_id == current_user.user_id).order_by(Order.created_at.desc()).all()
    
    result = []
    for order in orders:
        # 주문에 포함된 아이템 변환
        items_dto = []
        for item in order.items:
            items_dto.append(OrderItemDto(
                book_id=item.book_id,
                book_title=item.book.title,
                quantity=item.quantity,
                price=float(item.price)
            ))

        result.append(OrderDto(
            order_id=order.order_id,
            total_amount=float(order.total_amount),
            status=order.status,
            created_at=order.created_at.isoformat() if order.created_at else "",
            items=items_dto
        ))

    return APIResponse(isSuccess=True, message="주문 목록 조회 성공", payload=result)

@router.patch("/api/admin/orders/{order_id}", response_model=APIResponse)
def update_order_status(
    order_id: int,
    order_req: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        return APIResponse(isSuccess=False, message="관리자 권한이 필요합니다.")

    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        return APIResponse(isSuccess=False, message="주문을 찾을 수 없습니다.")
    
    # 상태 업데이트 (PENDING -> PAID -> SHIPPED 등)
    order.status = order_req.status
    db.commit()
    
    return APIResponse(isSuccess=True, message="주문 상태를 변경했습니다.")