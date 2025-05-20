from SQLAlchemy import create_engine, text

engine = create_engine("sqlite://BudgetBountry.db")

with engine.connect() as connection:
    connection.execute(text("QUERY"))
    connection.commit()