from flask import Flask, request, jsonify, json, render_template
import Final_Code_azureMonitoring as azureMonitoring
from flask_cors import CORS
import threading
import socket

app = Flask(__name__ ,static_folder="static", static_url_path="", template_folder="templates")
CORS(app)
# resources={r"/api/*": {"origins": "http://localhost:3000"}}
completeDataList = {}
completeDataList["subscriptionID"] = ""
completeDataList["resourceGroup"] = ""
completeDataList["ADF"] = ""
completeDataList["PipelineList"] = ""
completeDataList["lastTimeAfter"] = ""
completeDataList["lastTimeBefore"] = ""
completeDataList["RunId"] = ""


@app.route("/", methods=["GET"])
def index():
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    main_ip = f"http://{ip_addr}:5000"  # Assuming you want to include the port 5000
    print(main_ip)
    return render_template("index.html", main_ip=main_ip)


@app.route("/subscription", methods=["Get"])
def subscription():
    subscriptionList = azureMonitoring.getListOfSubscription()
    # return "Running"
    return jsonify(subscriptionList)


@app.route("/resourceGroup", methods=["Post", "Get"])
def resourceGroup():
    data = request.json
    subscriptionID = data["option"]
    completeDataList["subscriptionID"] = subscriptionID
    ResourceGroupList = azureMonitoring.SubscriptionDetail.getResourceGroup(
        subscriptionID
    )
    return jsonify(ResourceGroupList)


@app.route("/ADF", methods=["Post", "Get"])
def dataFactory():
    data = request.json
    subscriptionID = data["subscription"]
    resourceGroup = data["ResourceGroup"]
    completeDataList["resourceGroup"] = resourceGroup
    ADFList = azureMonitoring.SubscriptionDetail.getListOfADFs(
        subscriptionID, resourceGroup
    )
    return jsonify(ADFList)


@app.route("/lastTimeAfter", methods=["Post", "Get"])
def lastTimeAfter():
    data = request.json
    completeDataList["lastTimeAfter"] = data["input"]
    return jsonify("LastTimeAfter success")


@app.route("/lastTimeBefore", methods=["Post", "Get"])
def lastTimebefore():
    data = request.json
    completeDataList["lastTimeBefore"] = data["input"]
    return jsonify("LastTimeBefore success")


@app.route("/Pipeline", methods=["Post", "Get"])
def Pipeline():
    print("Yes")
    data = request.json
    print(data)
    print("No")
    print(data["ADF"])
    completeDataList["ADF"] = data["ADF"]
    print(completeDataList)
    PipelineList = azureMonitoring.SubscriptionDetail.getListOfPipelines(
        completeDataList["resourceGroup"],
        completeDataList["ADF"],
        completeDataList["subscriptionID"],
    )
    return jsonify(PipelineList)


# @app.route('/Pipelines', methods=['Post','Get'])
# def Pipelines():
#     PipelineList = azureMonitoring.SubscriptionDetail.getListOfPipelines(completeDataList["resourceGroup"],completeDataList["ADF"],completeDataList["subscriptionID"])
#     completeDataList["PipelineList"] = PipelineList
#     completeData = azureMonitoring.RunHistory.get_master_pipeline_adf(completeDataList["subscriptionID"],completeDataList["resourceGroup"],completeDataList["ADF"],completeDataList["PipelineList"],completeDataList["lastTimeAfter"],completeDataList["lastTimeBefore"])
#     return jsonify(completeData)
#     # return jsonify(PipelineList)
results = []


@app.route("/Pipelines", methods=["POST", "GET"])
def Pipelines():
    adf_list = request.json
    print(adf_list)

    threads = []
    for adf in adf_list:
        print(adf)
        print(type(adf))
        thread = threading.Thread(target=process_adf, args=(adf,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    complete_data_list = results
    print(complete_data_list)
    return jsonify(complete_data_list)


def process_adf(adf):
    pipeline_list = azureMonitoring.SubscriptionDetail.getListOfPipelines(
        completeDataList["resourceGroup"], adf, completeDataList["subscriptionID"]
    )
    completeDataList["PipelineList"] = pipeline_list
    complete_data = azureMonitoring.RunHistory.get_master_pipeline_adf(
        completeDataList["subscriptionID"],
        completeDataList["resourceGroup"],
        adf,
        completeDataList["PipelineList"],
        completeDataList["lastTimeAfter"],
        completeDataList["lastTimeBefore"],
    )
    if len(complete_data) > 0:
        results.append(complete_data)


@app.route("/ActivityList", methods=["Post", "Get"])
def ActivityList():
    data = request.json
    # print(data)
    completeDataList["ADF"] = data["ADF"]
    completeDataList["RunId"] = data["RunID"]
    ActivityList = azureMonitoring.RunHistory.get_activity_list(
        completeDataList["subscriptionID"],
        completeDataList["resourceGroup"],
        completeDataList["ADF"],
        completeDataList["RunId"],
        completeDataList["lastTimeAfter"],
        completeDataList["lastTimeBefore"],
    )
    return jsonify(ActivityList)


if __name__ == "__main__":
    # app.run(debug=True)
    # Pipelines()
    app.run(host="0.0.0.0", port=5000, debug=True)
