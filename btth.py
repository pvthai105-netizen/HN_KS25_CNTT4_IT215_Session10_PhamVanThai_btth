from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI()

DATABASE_URL = "mysql+pymysql://root:123456$@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

class ShipmentModel(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tracking_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="PREPARING")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(tracking_number: str, db: Session = Depends(get_db)):
    
    shipment = (db.query(ShipmentModel).filter(ShipmentModel.tracking_number == tracking_number).first())

    if shipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã vận đơn này đã được khởi tạo trước đó"
        )

    new_shipment = ShipmentModel(tracking_number=tracking_number)

    db.add(new_shipment)
    db.commit()

    return {
        "message": "Tạo mã vận đơn thành công",
        "data": new_shipment
    }


@app.get("/shipments", status_code=status.HTTP_200_OK)
def get_shipments(db: Session = Depends(get_db)):
    shipments = db.query(ShipmentModel).all()

    return shipments
