class NormalizationNode extends BaklavaJS.Core.Node {

    type = "NormalizationNode";
    name = "Normalization";
    constructor() {
        super();
        this.addInputInterface("Input Data");
        this.addOption("Q1", "CheckboxOption");
        this.addOption("Q2", "CheckboxOption");
        this.addOption("Q3", "CheckboxOption");
        this.addOption("Q4", "CheckboxOption");
        this.addOption("Q5", "CheckboxOption");
        this.addOption("Normalization Method", "SelectOption", "Normalization Method", undefined,{
            items: ["Min-Max",
                    "Z-Score"]
        });
        this.addOption("Replace original data", "CheckboxOption");
        this.addOutputInterface("Result");
    }

    calculate() {
        //construct parameter object
        const column_names = ["Q1", "Q2", "Q3", "Q4", "Q5"];
        let output_option = this.getOptionValue("Replace original data");
        let algorithm_config = {
            "function_name": "normalisation",
            "column_selected": [],
            "Method": this.getOptionValue("Normalization Method"),
            "Output option": "",
            "result_path": "public/test.csv"
        };
        for (const column_name of column_names){
            if (this.getOptionValue(column_name) == true)
                algorithm_config.column_selected.push(column_name);
        }
        if (output_option == true)
            algorithm_config["Output option"] = "on";

        const form = document.createElement('form');
        form.method = 'post';
        form.id = 'norm';
        form.action = process_url;

        for (const key in algorithm_config){
            if (algorithm_config.hasOwnProperty(key)){
                const hiddenField = document.createElement("input");
                hiddenField.type = "hidden";
                hiddenField.name = key;
                hiddenField.value = algorithm_config[key];

                form.appendChild(hiddenField);
            }
        }

        document.body.appendChild(form);

        let forms = document.getElementById("norm");
        form.addEventListener('submit', function(event) {
            event.preventDefault();    // prevent page from refreshing
            const formData = new FormData(forms);  // grab the data inside the form fields
            fetch('/node_editor/processing', {   // assuming the backend is hosted on the same server
                method: 'POST',
                body: formData,
            }).then(function(response) {
                // do something with the response if needed.
                // If you want the table to be built only after the backend handles the request and replies, call buildTable() here.
            });
        });

        form.submit();
    }
}
