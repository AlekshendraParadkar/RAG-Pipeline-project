from generate import generate_answer

def test_generate_answer():
    question = "What is the National Highways Excellence Awards explain in detail?"
    response = generate_answer(question)
    print("Question:", question)
    print("Answer:", response)

if __name__ == "__main__":
    test_generate_answer()
