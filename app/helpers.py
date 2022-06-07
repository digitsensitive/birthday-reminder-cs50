
def split_date(date):
    """Split date YYYY-MM-DD into seperate values 
    As a return value you get a dictionary with three key-value pairs:
    Keys: day, month and year
    """

    # Split the date using the string split method with the separator -
    year, month, day = date.split('-')

    # Return a dictionary
    return {'day': day, 'month': month, 'year': year}
