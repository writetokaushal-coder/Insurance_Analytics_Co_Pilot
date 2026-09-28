import pandas as pd
from src.database import engine
from sqlalchemy import text








query = """
SELECT TOP 10 POLICY_ID
FROM analytics.renewal_model_features
"""
with engine.connect() as connection:
    df = pd.read_sql(query, engine)

print(df)    

#     result = connection.execute(
#         text(
#             "SELECT DB_NAME()"
#         )
#     ).scalar()

#     print(result)

# test repository

# from src.repositories.renewal_repository import (
#     get_renewal_features
# )

# df = get_renewal_features(
#     "POL000051250"
# )

# print(df.shape)

# print(
#     df[
#         [
#             "POLICY_ID",
#             "CUSTOMER_ID",
#             "PREMIUM_INCREASE_PCT"
#         ]
#     ]
# )


#  POL000051250
# 1  POL000017253
# 2  POL000108220
# 3  POL000068626
# 4  POL000134055
# 5  POL000003688
# 6  POL000131003
# 7  POL000052341
# 8  POL000001288
# 9  POL000031423