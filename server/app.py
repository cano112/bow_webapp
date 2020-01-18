from bow import bow_facade
from flask import Flask, request, send_file, make_response
from flask_cors import CORS, cross_origin
from skimage import io, img_as_ubyte
import uuid
import tempfile

DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

PR_PATH_TEMPLATE = "{}/pr_{}.png"
RES_PATH_TEMPLATE = "{}/res_{}.png"


@app.errorhandler(500)
def internal_error(error):
    return "Internal server error occurred. Please check if you have uploaded valid x-ray & mask images.", 500


@app.route("/upload-image", methods=["POST"])
@cross_origin()
def upload_image():
    temp_dir = tempfile.gettempdir()
    id = uuid.uuid4().hex
    xray_path = "{}/xray_{}.png".format(temp_dir, id)
    mask_path = "{}/mask_{}.png".format(temp_dir, id)

    if request.files['xray'].content_type != 'image/png' or request.files['mask'].content_type != 'image/png':
        return 'Invalid file format. Only PNG files are accepted.', 400

    request.files['xray'].save(xray_path)
    request.files['mask'].save(mask_path)


    xray = io.imread(xray_path)
    mask = io.imread(mask_path)

    pr, m = bow_facade.get_image(xray, mask)

    pr_path = PR_PATH_TEMPLATE.format(temp_dir, id)
    res_path = RES_PATH_TEMPLATE.format(temp_dir, id)
    io.imsave(pr_path, img_as_ubyte(pr))
    io.imsave(res_path, img_as_ubyte(m))
    response = make_response(str(id), 201)
    response.mimetype = "text/plain"
    return response


@app.route("/pr", methods=["GET"])
@cross_origin()
def download_pr():
    temp_dir = tempfile.gettempdir()
    if 'id' not in request.args:
        return "No id provided", 400
    path = PR_PATH_TEMPLATE.format(temp_dir, request.args.get('id'))
    return send_file(path, mimetype='image/png')


@app.route("/res", methods=["GET"])
@cross_origin()
def download_res():
    temp_dir = tempfile.gettempdir()
    if 'id' not in request.args:
        return "No id provided", 400
    path = RES_PATH_TEMPLATE.format(temp_dir, request.args.get('id'))
    return send_file(path, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
