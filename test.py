x=["ss","ss","ss","tt"]
y=""
u = "||"
y = u.join(x)
print(y)
test="bonjour:-#bonjour:-#y a-t-il un problème:-#bonjour:-#:-#bonjour:-#bonjour:-#comment allez-vous:-#comment allez vous:-#salam:-#bonjour:-#salut:-#salut:-#salut:-#comment vas-tu :-#tu vas bien:-#esta bien:-#bonjour:-#bonjour, comment vas-tu:-#ana||:-# comment vas-tu ? :-#salut"
print("............")
t=test.split(":-#")
print(t)
def contains_special_sequence(message, sequence="|#^"):
    return sequence in message
print(".............")
# Example usage
message = " test message|#^ hhgciih kh"
if "|#^" in message:
    message=message.replace("|#^", "")
    print(message)
