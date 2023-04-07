class DataProcessingNode extends BaklavaJS.Core.Node {

    type = "data_processing";
    name = "DataProcessing";
    // fetch('/algorithms/data_proc_para_cfg.json')
    //     .then(response=>response.json())
    constructor() {
        super();
        this.addInputInterface("Input Data");
        this.addOutputInterface("Result");
        this.addOption("Operation", "SelectOption", {
            selected: "",
            items: ["Outlier Handling",
                    "Tail shrinkage and truncation processing"
            ]});
    }

    process() {

    }

}
