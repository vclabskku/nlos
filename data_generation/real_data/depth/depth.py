
class Depth():

    def __init__(self, config):

        self.config = config

    def get_depth_image(self):

        depth_image = np.zeros(dtype=np.uint8, shape=(224, 224, 3))

        return depth_image