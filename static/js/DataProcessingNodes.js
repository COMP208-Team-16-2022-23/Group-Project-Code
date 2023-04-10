class DataTransformNode extends BaklavaJS.Core.Node {

    type = "DataTransformNode";
    name = "DataTransform";
    constructor() {
        super();
        this.addInputInterface("Input Dataset");
        this.addInputInterface("Selected Columns");
        this.addOption("New Filename", "InputOption");

        this.addOption("transform_method", "SelectOption", "Method", undefined,{
            items: [
                "FFT",
                "IFFT"
            ]
        });

        this.addOutputInterface("New File");
    }

    calculate() {
        //construct parameter object
        let algorithm_config = {
            "function_name": "data_transform",
            "file_path": this.getInterface("Input Dataset").value,
            "column_selected": this.getInterface("Selected Columns").value,

            "transform_method": this.getOptionValue("transform_method"),

            "result_path": this.getOptionValue("New Filename") + '.csv'
        };
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
    }
}

class DimensionReductionNode extends BaklavaJS.Core.Node {

    type = "DimensionReductionNode";
    name = "DimensionReduction";
    constructor() {
        super();
        this.addInputInterface("Input Dataset");
        this.addInputInterface("Selected Columns");
        this.addOption("New Filename", "InputOption");

        this.addOption("method", "SelectOption", "Method", undefined,{
            items: [
                "PCA",
                "LDA"
            ]
        });
        this.addOption("n_components", "NumberOption");
        this.addOption("target_column", "InputOption", undefined, undefined, { displayName: "Target Column"});

        this.addOutputInterface("New File");
    }

    calculate() {
        //construct parameter object
        let algorithm_config = {
            "function_name": "dimension_reduction",
            "file_path": this.getInterface("Input Dataset").value,
            "column_selected": this.getInterface("Selected Columns").value,

            "method": this.getOptionValue("method"),
            "n_components": this.getOptionValue("n_components"),
            "target_column": null,

            "result_path": this.getOptionValue("New Filename") + '.csv'
        };
        if (this.getOptionValue("target_column"))
            algorithm_config.target_column = this.getOptionValue("target_column").split(",");
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
    }
}

class MissingValueHandlingNode extends BaklavaJS.Core.Node {

    type = "MissingValueHandlingNode";
    name = "MissingValueHandling";
    constructor() {
        super();
        this.addInputInterface("Input Dataset");
        this.addInputInterface("Selected Columns");
        this.addOption("New Filename", "InputOption");

        this.addOption("identification_method", "SelectOption", "Identification Method", undefined,{
            items: [
                "empty",
                "space",
                "nan-numeric value",
                "'None'"
            ]
        });
        this.addOption("filling_method", "SelectOption", "Filling Method", undefined,{
            items: [
                "mean",
                "median",
                "mode"
            ]
        });
        this.addOutputInterface("New File");
    }

    calculate() {
        //construct parameter object
        let algorithm_config = {
            "function_name": "missing_value_handling",
            "file_path": this.getInterface("Input Dataset").value,
            "column_selected": this.getInterface("Selected Columns").value,
            "identification_method": this.getOptionValue("identification_method"),
            "filling_method": this.getOptionValue("filling_method"),
            "result_path": this.getOptionValue("New Filename") + '.csv'
        };
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
    }
}

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

class OutlierHandlingNode extends BaklavaJS.Core.Node {

    type = "OutlierHandlingNode";
    name = "OutlierHandling";
    constructor() {
        super();
        this.addInputInterface("Input Dataset");
        this.addInputInterface("Selected Columns");
        this.addOption("New Filename", "InputOption");
        this.addOption("Detection method", "SelectOption", "Handling Method", undefined,{
            items: ["3-sigma",
                "IQR",
                "MAD"]
        });
        this.addOption("Processing method", "SelectOption", "Processing Method", undefined,{
            items: ["set to null",
                "set to mean",
                "set to median"]
        });
        this.addOutputInterface("New File");
    }

    calculate() {
        //construct parameter object
        let algorithm_config = {
            "function_name": "outlier_handling",
            "file_path": this.getInterface("Input Dataset").value,
            "column_selected": this.getInterface("Selected Columns").value,
            "Detection method": this.getOptionValue("Detection method"),
            "Processing method": this.getOptionValue("Processing method"),
            "result_path": this.getOptionValue("New Filename") + '.csv'
        };
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
    }
}

class SampleBalancingNode extends BaklavaJS.Core.Node {

    type = "SampleBalancingNode";
    name = "SampleBalancing";
    constructor() {
        super();
        this.addInputInterface("Input Dataset");
        this.addInputInterface("Selected Columns");
        this.addOption("New Filename", "InputOption");

        this.addOption("balancing_method", "SelectOption", "Balancing Method", undefined,{
            items: [
                "undersample",
                "oversample",
                "combined"
            ]
        });
        this.addOption("target_column", "InputOption", undefined, undefined, { displayName: "Target Column"});

        this.addOutputInterface("New File");
    }

    calculate() {
        //construct parameter object
        let algorithm_config = {
            "function_name": "sample_balancing",
            "file_path": this.getInterface("Input Dataset").value,
            "column_selected": this.getInterface("Selected Columns").value,

            "balancing_method": this.getOptionValue("balancing_method"),
            "target_column": null,

            "result_path": this.getOptionValue("New Filename") + '.csv'
        };
        if (this.getOptionValue("target_column"))
            algorithm_config.target_column = this.getOptionValue("target_column").split(",");
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
    }
}

class TailShrinkageAndTruncationProcessingNode extends BaklavaJS.Core.Node {

    type = "TailShrinkageAndTruncationProcessingNode";
    name = "TailShrinkage&TruncationProcessing";
    constructor() {
        super();
        this.addInputInterface("Input Dataset");
        this.addInputInterface("Selected Columns");
        this.addOption("New Filename", "InputOption");

        this.addOption("method_selection", "SelectOption", "Method", undefined,{
            items: [
                "tail_shrinkage",
                "tail_truncation"
            ]
        });
        this.addOption("upper_limit", "NumberOption");
        this.addOption("lower_limit", "NumberOption");
        this.addOption("processing_method", "SelectOption", "Processing Method", undefined,{
            items: [
                "delete_value",
                "delete_row"
            ]
        });
        this.addOutputInterface("New File");
    }

    calculate() {
        //construct parameter object
        let algorithm_config = {
            "function_name": "tail_shrinkage_or_truncation_processing",
            "file_path": this.getInterface("Input Dataset").value,
            "column_selected": this.getInterface("Selected Columns").value,

            "method_selection": this.getOptionValue("method_selection"),
            "upper_limit": this.getOptionValue("upper_limit"),
            "lower_limit": this.getOptionValue("lower_limit"),
            "processing_method": this.getOptionValue("processing_method"),

            "result_path": this.getOptionValue("New Filename") + '.csv'
        };
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
    }
}
