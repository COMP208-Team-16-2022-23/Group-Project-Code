class DataProcessingNode extends BaklavaJS.Core.Node {

    type = "data_processing";
    name = "DataProcessing";

    constructor() {
        super();
        this.algo_names = [];
        this.file_paths = [];
        for (const algo of processing) {
            this.algo_names.push(algo.name);
            // this.file_paths.push(dataset.file_path);
        }
        this.addInputInterface("Input Data");
        this.addOutputInterface("Result");
        this.addOption("Processing Method", "SelectOption", this.algo_names[0], undefined, {
            items: this.algo_names
        });
    }

    calculate() {

    }

}
