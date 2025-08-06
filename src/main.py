import torch


DEFAULT_FONT = "./asset/PoorStory-Regular.ttf"


class ChatEntity:
    def __init__(self, text="lorem ipsum dolar shit", animation="fade-in", font=DEFAULT_FONT, author="llama", timestamp=0):
        self.text = text
        self.animation = animation
        self.author = author
        self.timestamp = timestamp
        self.font = font


# main logic
def main():
    # check for CUDA use
    try:
        print("CUDA availability: " + str(torch.cuda.is_available()))
        print(torch.cuda.get_device_name(0))
    except Exception as err:
        print(err)
        print("CUDA not working. quit")
        quit()
