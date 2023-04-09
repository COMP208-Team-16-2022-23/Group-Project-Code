class NormalizationNode extends BaklavaJS.Core.Node {

    type = "NormalizationNode";
    name = "Normalization";
    constructor() {
        super();
        this.addInputInterface("Input Dataset");
        this.addInputInterface("Selected Columns");
        this.addOption("New Filename", "InputOption");
        this.addOption("Normalization Method", "SelectOption", "Normalization Method", undefined,{
            items: ["Min-Max",
                    "Z-Score"]
        });
        this.addOption("Replace original data", "CheckboxOption");
        this.addOutputInterface("New File");
    }

    calculate() {
        //construct parameter object
        let output_option = this.getOptionValue("Replace original data");
        let algorithm_config = {
            "function_name": "normalisation",
            "file_path": this.getInterface("Input Dataset").value,
            "column_selected": this.getInterface("Selected Columns").value,
            "Method": this.getOptionValue("Normalization Method"),
            "Output option": "",
            "result_path": this.getOptionValue("New Filename") + '.csv'
        };
        if (output_option == true)
            algorithm_config["Output option"] = "on";
        var res;
        //call url_for('node_editor.processing')
        $.ajax({

            type: "POST",
            url: process_url,
            data: JSON.stringify(algorithm_config),
            contentType: "application/json",
            dataType: 'json',
            success: function(response){
                res = response.payload;
                console.log(res);
                this.getInterface("New File").value=res;
            }.bind(this)
        });
        // const form = document.createElement('form');
        // form.method = 'post';
        // form.id = 'norm';
        // form.action = process_url;
        //
        // for (const key in algorithm_config){
        //     if (algorithm_config.hasOwnProperty(key)){
        //         const hiddenField = document.createElement("input");
        //         hiddenField.type = "hidden";
        //         hiddenField.name = key;
        //         hiddenField.value = algorithm_config[key];
        //
        //         form.appendChild(hiddenField);
        //     }
        // }
        //
        // document.body.appendChild(form);

        // form.submit();
    }
}
