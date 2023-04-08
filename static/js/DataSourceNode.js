class DataSourceNode extends BaklavaJS.Core.Node {

    type = "data_source";
    name = "Data";
    constructor() {
        super();
        this.file_names = [];
        this.file_paths = [];
        for (const dataset of datasets) {
            this.file_names.push(dataset.file_name);
            this.file_paths.push(dataset.file_path);
        }
        console.log(this.file_paths);
        this.addOutputInterface("Output");
        this.addOption("Operation", "SelectOption", "Select your Data", undefined,
            {items: this.file_names}
        );
    }

    calculate() {
        const operation = this.getOptionValue("Operation");
        let result;
        var index = this.file_names.indexOf(operation);
        result = this.file_paths[index];
        this.getInterface("Output").value = result;
    }

}

class TestNode extends BaklavaJS.Core.Node{

    type = "TestNode";
    name = "DisplayTest";

    constructor() {
        super();
        this.addInputInterface("Input");
        this.addOption("Text", "TextOption");
    }

     calculate() {
        let text = this.getInterface("Input").value;
        console.log(text);
        this.setOptionValue("Text", text);
    }

}

