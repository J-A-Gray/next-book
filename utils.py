def convert_row_to_dict(row):
    row_dict = {}
    for column in row.__table__.columns:
        row_dict[column.name] = str(getattr(row, column.name))

    return row_dict