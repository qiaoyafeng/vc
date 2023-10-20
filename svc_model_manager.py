from inference.infer_tool import Svc


model_name = "trained/G_160000.pth"
config_name = "trained/config.json"
cluster_model_path = "trained/G_160000.pth"

hxq_svc_model = Svc(model_name, config_name, cluster_model_path=cluster_model_path)