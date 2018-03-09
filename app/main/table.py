from flask_table import Table, Col, DatetimeCol, BoolCol


class BlockchainTable(Table):
    # Class to format the table
    classes = ['table', 'table-striped']

    from_user = Col('From')
    to_user = Col('To')
    amount = Col('Amount')
    timestamp = DatetimeCol('Timestamp', datetime_format='full')
    nonce = Col('Nonce')
    miner_verify = BoolCol('Transaction Verified')
