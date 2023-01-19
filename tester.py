from databases import caDB

res = caDB.get_all_posts('orders')

for i in res:
    print(i)