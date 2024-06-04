from gluoncv.model_zoo import get_model
import matplotlib.pyplot as plt
from mxnet import gluon, nd, image
from mxnet.gluon.data.vision import transforms
from gluoncv import utils
from PIL import Image
import io
import flask
from flask import request, render_template, jsonify

app = flask.Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        if request.files.get("img"):
            img = Image.open(io.BytesIO(request.files["img"].read()))
            transform_fn = transforms.Compose([
                transforms.Resize(32),
                transforms.CenterCrop(32),
                transforms.ToTensor(),
                transforms.Normalize([0.4914, 0.4822, 0.4465], [0.2023, 0.1994, 0.2010])
            ])
            img = transform_fn(nd.array(img))
            net = get_model('cifar_resnet20_v1', pretrained=True)
            pred = net(img.expand_dims(axis=0))
            class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                           'dog', 'frog', 'horse', 'ship', 'truck']
            icons = ['✈️', '🚗', '🐦', '🐱', '🦌', '🐶', '🐸', '🐴', '🚢', '🚚']
            ind = nd.argmax(pred, axis=1).astype('int')
            prediction = 'The input picture is classified as [%s] %s, with probability %.3f.' % (
                class_names[ind.asscalar()], icons[ind.asscalar()], nd.softmax(pred)[0][ind].asscalar())
            return jsonify({"prediction": prediction})
    return jsonify({"error": "No image uploaded"})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
