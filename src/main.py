from textnode import TextNode, TextType


def main():
    dummy_text = TextNode(
        "I like Autechre and house music", TextType.LINK, "https://autechre.ws"
    )

    print(dummy_text)


if __name__ == "__main__":
    main()
