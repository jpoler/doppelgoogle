import insert
# res = insert.DomainInserter.create_or_update_object(name="Bob")


res = insert.DomainInterface.get_node("Frank")
print(res)
print(dir(res))
