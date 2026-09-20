from flask import Flask, render_template, request, redirect, url_for
import pickle
import numpy as np
import os

app = Flask(__name__)


model = None


def load_model():
    global model
    try:
        filename = 'model/predictor.pickle'
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                model = pickle.load(file)
            print("Model loaded successfully")
        else:
            print("Model file not found")
            model = None
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None


load_model()


def prediction(feature_list):
    if model is None:
       
        return 50000  
    
    try:
       
        if len(feature_list) < 32:
            feature_list.extend([0] * (32 - len(feature_list)))
        
        pred_value = model.predict([feature_list])
        return pred_value[0]
    except Exception as e:
        print(f"Error making prediction: {e}")
        return 50000  


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  
        try:
            print("POST request received")
            print("Form data:", request.form)
            
           
            ram = int(request.form.get('ram', 0))
            weight = float(request.form.get('weight', 0))
            company = request.form.get('company', '')
            typename = request.form.get('typename', '')
            opsys = request.form.get('opsys', '')
            cpu = request.form.get('cpuname', '')
            gpu = request.form.get('gpuname', '')
            touchscreen = request.form.get('touchscreen') is not None
            ips = request.form.get('ips') is not None
            
            print(f"Parsed data: ram={ram}, weight={weight}, company={company}, typename={typename}, opsys={opsys}, cpu={cpu}, gpu={gpu}")
            
           
            if not all([ram, weight, company, typename, opsys, cpu, gpu]):
                print("Validation failed - missing required fields")
                return render_template("index.html", error="Please fill in all required fields")
            
            feature_list = [
                ram,
                weight,
                1 if touchscreen else 0,
                1 if ips else 0
            ]
            
            company_list = ['acer', 'apple', 'asus', 'dell', 'hp', 'lenovo', 'msi', 'other', 'toshiba']
            typename_list = ['2in1convertible', 'gaming', 'netbook', 'notebook', 'ultrabook', 'workstation']
            opsys_list = ['linux', 'mac', 'other', 'windows']
            cpu_list = ['amd', 'intelcorei3', 'intelcorei5', 'intelcorei7', 'other']
            gpu_list = ['amd', 'arm', 'intel', 'nvidia']
            
            def traverse(list_name, value):
                for item in list_name:
                    feature_list.append(1 if item == value else 0)
            
            traverse(company_list, company)
            traverse(typename_list, typename)
            traverse(opsys_list, opsys)
            traverse(cpu_list, cpu)
            traverse(gpu_list, gpu)
            
            
            pred = prediction(feature_list)
            print(f"Initial prediction: {pred}")
            
           
            if model is not None:
                pred = pred * 351.70 
                pred = np.round(pred)
                print(f"ML model prediction: {pred}")
            else:
                
                base_price = 30000
                price_multiplier = 1.0
                
                
                price_multiplier += (ram - 4) * 0.1
                
                
                if company == 'apple':
                    price_multiplier *= 2.0
                elif company in ['dell', 'hp']:
                    price_multiplier *= 1.3
                elif company in ['asus', 'msi']:
                    price_multiplier *= 1.2
                
                
                if typename == 'gaming':
                    price_multiplier *= 1.5
                elif typename == 'workstation':
                    price_multiplier *= 1.8
                elif typename == 'ultrabook':
                    price_multiplier *= 1.4
                
                pred = base_price * price_multiplier
                pred = round(pred)
                print(f"Rule-based prediction: {pred}")

            
            print(f"Redirecting to result with pred={pred}")
            return redirect(url_for('result', pred=pred))
            
        except ValueError as e:
            return render_template("index.html", error="Please enter valid numbers for RAM and Weight")
        except Exception as e:
            return render_template("index.html", error="An error occurred. Please try again.")

    return render_template("index.html")


@app.route('/result')
def result():
    pred = request.args.get('pred', default=0, type=float)
    model_status = "ML Model" if model is not None else "Rule-based"
    print(f"Result route called with pred={pred}, model_status={model_status}")
    return render_template("index1.html", pred=pred, model_status=model_status)

if __name__ == '__main__':
    app.run(debug=True)
