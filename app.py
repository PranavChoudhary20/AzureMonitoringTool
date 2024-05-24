from flask import Flask, request, jsonify, json, render_template
import Final_Code_azureMonitoring as azureMonitoring
from flask_cors import CORS
import threading
import socket

app = Flask(__name__)
CORS(app)
Flag = 1
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


@app.route("/SelectedOption", methods=["POST"])
def selectedoption():
    global Flag
    data = request.get_json()
    setflag = data["flag"]
    Flag = setflag
    print(Flag)
    return jsonify({"Flag": setflag})


@app.route("/ADF", methods=["Post", "Get"])
def WorkSpace():
    data = request.json
    subscriptionID = data["subscription"]
    resourceGroup = data["ResourceGroup"]
    completeDataList["resourceGroup"] = resourceGroup
    WorkSpaceList = azureMonitoring.SubscriptionDetail.getListOfWorkspaces(
        subscriptionID, resourceGroup
    )
    # if Flag == 0:
    #     return jsonify(WorkSpaceList[0])
    # elif Flag ==1:
    #     return jsonify(WorkSpaceList[1])
    # elif Flag ==3:

    return jsonify(WorkSpaceList)


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
    data = request.json
    completeDataList["ADF"] = data["adfList"][0]
    if Flag == 0:
        PipelineList = azureMonitoring.SubscriptionDetail.getListOfADFPipelines(
            completeDataList["resourceGroup"],
            completeDataList["ADF"],
            completeDataList["subscriptionID"],
        )
    elif Flag == 1:
        PipelineList = azureMonitoring.SubscriptionDetail.getListOfASAPipelines(
            completeDataList["resourceGroup"],
            completeDataList["ADF"],
            completeDataList["subscriptionID"],
        )
    return jsonify(PipelineList)


# VivekSharma
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
    WorkSpacelist = request.json

    threads = []
    for WorkSpace in WorkSpacelist:
        thread = threading.Thread(target=ProcessWorkSpace(WorkSpace), args=(WorkSpace,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    complete_data_list = results
    return jsonify(complete_data_list)


def ProcessWorkSpace(WorkSpace):
    if Flag == 0:
        pipeline_list = azureMonitoring.SubscriptionDetail.getListOfADFPipelines(
            completeDataList["resourceGroup"],
            WorkSpace,
            completeDataList["subscriptionID"],
        )
        completeDataList["PipelineList"] = pipeline_list
        complete_data = azureMonitoring.RunHistory.GetADFMasterPipeline(
            completeDataList["subscriptionID"],
            completeDataList["resourceGroup"],
            WorkSpace,
            completeDataList["PipelineList"],
            completeDataList["lastTimeAfter"],
            completeDataList["lastTimeBefore"],
        )
        if len(complete_data) > 0:
            results.append(complete_data)
    elif Flag == 1:
        pipeline_list = azureMonitoring.SubscriptionDetail.getListOfASAPipelines(
            completeDataList["resourceGroup"],
            WorkSpace,
            completeDataList["subscriptionID"],
        )
        completeDataList["PipelineList"] = pipeline_list
        complete_data = azureMonitoring.RunHistory.GetASAMasterPipeline(
            completeDataList["subscriptionID"],
            completeDataList["resourceGroup"],
            WorkSpace,
            completeDataList["PipelineList"],
            completeDataList["lastTimeAfter"],
            completeDataList["lastTimeBefore"],
        )
        if len(complete_data) > 0:
            results.append(complete_data)


@app.route("/ActivityList", methods=["Post", "Get"])
def ActivityList():
    if Flag == 0:
        data = request.json
        completeDataList["ADF"] = data["ADF"]
        completeDataList["RunId"] = data["RunID"]
        ActivityList = azureMonitoring.RunHistory.GetADFActivityList(
            completeDataList["subscriptionID"],
            completeDataList["resourceGroup"],
            completeDataList["ADF"],
            completeDataList["RunId"],
            completeDataList["lastTimeAfter"],
            completeDataList["lastTimeBefore"],
        )
    elif Flag == 1:
        data = request.json
        completeDataList["ADF"] = data["ADF"]
        completeDataList["RunId"] = data["RunID"]
        completeDataList["PipelineName"] = data["PipelineName"]
        ActivityList = azureMonitoring.RunHistory.GetASAActivityList(
            completeDataList["subscriptionID"],
            data["PipelineName"],
            data["ADF"],
            data["RunID"],
            completeDataList["lastTimeAfter"],
            completeDataList["lastTimeBefore"],
        )
    return jsonify(ActivityList)


if __name__ == "__main__":
    # app.run(debug=True)
    # Pipelines()
    app.run(host="0.0.0.0", port=5000, debug=True)
