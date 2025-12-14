from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cart, CartItem, Book, User
from app.schemas import APIResponse, CartItemCreate, CartItemDto, CartListResponse, CartItemUpdate
from app.dependencies import get_current_user
router = APIRouter()

# 1. 장바구니에 담기
@router.post("/api/carts/items", response_model=APIResponse)
def add_to_cart(
    item_req: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 유저의 장바구니 찾기 (없으면 생성)
    cart = db.query(Cart).filter(Cart.user_id == current_user.user_id).first()
    if not cart:
        cart = Cart(user_id=current_user.user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # 2. 이미 담긴 책인지 확인
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.cart_id,
        CartItem.book_id == item_req.book_id
    ).first()

    if existing_item:
        # 이미 있으면 수량 추가
        existing_item.quantity += item_req.quantity
    else:
        # 없으면 새로 추가
        new_item = CartItem(
            cart_id=cart.cart_id,
            book_id=item_req.book_id,
            quantity=item_req.quantity
        )
        db.add(new_item)
    
    db.commit()
    return APIResponse(isSuccess=True, message="장바구니에 담았습니다.")

# 2. 장바구니 조회
@router.get("/api/carts", response_model=APIResponse[CartListResponse])
def get_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(Cart.user_id == current_user.user_id).first()
    if not cart:
        return APIResponse(isSuccess=True, message="장바구니가 비어있습니다.", payload={"cart_id": 0, "items": [], "total_price": 0})

    # 아이템 목록 가져오기 (책 정보 포함)
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.cart_id).all()
    
    dtos = []
    total_price = 0
    for item in cart_items:
        dtos.append(CartItemDto(
            cart_item_id=item.cart_item_id,
            book_id=item.book_id,
            book_title=item.book.title, # 관계형 데이터 접근
            quantity=item.quantity,
            price=float(item.book.price)
        ))
        total_price += (float(item.book.price) * item.quantity)

    return APIResponse(
        isSuccess=True,
        message="장바구니 조회 성공",
        payload={
            "cart_id": cart.cart_id,
            "items": dtos,
            "total_price": total_price
        }
    )

# 3. 장바구니 아이템 삭제
@router.delete("/api/carts/items/{cart_item_id}", response_model=APIResponse)
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 내 장바구니의 아이템인지 확인 필요
    item = db.query(CartItem).join(Cart).filter(
        CartItem.cart_item_id == cart_item_id,
        Cart.user_id == current_user.user_id
    ).first()

    if not item:
        return APIResponse(isSuccess=False, message="삭제할 아이템을 찾을 수 없습니다.")
    
    db.delete(item)
    db.commit()
    return APIResponse(isSuccess=True, message="장바구니에서 삭제했습니다.")

@router.patch("/api/carts/items/{cart_item_id}", response_model=APIResponse)
def update_cart_item_quantity(
    cart_item_id: int,
    cart_req: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(CartItem).join(Cart).filter(
        CartItem.cart_item_id == cart_item_id,
        Cart.user_id == current_user.user_id
    ).first()

    if not item:
        return APIResponse(isSuccess=False, message="아이템을 찾을 수 없습니다.")
    
    if cart_req.quantity <= 0:
        db.delete(item) # 0개 이하면 삭제 처리
        message = "상품을 장바구니에서 삭제했습니다."
    else:
        item.quantity = cart_req.quantity
        message = "수량을 변경했습니다."
        
    db.commit()
    return APIResponse(isSuccess=True, message=message)