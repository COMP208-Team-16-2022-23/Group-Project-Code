class DataSourceNode extends BaklavaJS.Core.Node {

    type = "data_source";
    name = "Data";

    constructor() {
        super();
        this.file_names = [];
        this.file_paths = [];
        for (const dataset of datasets) {
            this.file_names.push(dataset.file_names);
            this.file_paths.push(dataset.file_paths);
        }
        this.addOutputInterface("Output");
        this.addOption("Operation", "SelectOption",{
            items: this.file_names
        });
    }

    calculate() {
        const operation = this.getOptionValue("Operation").selected;
        let result;
        var index = this.file_names.indexOf(operation);
        result = this.file_paths[index];
        this.getInterface("Output").value = result;
    }

}

class MathNode extends BaklavaJS.Core.Node{

    type = "MathNode";
    name = "Math";

    constructor() {
        super();
        this.addInputInterface("Number 1", "NumberOption", 1);
        this.addInputInterface("Number 2", "NumberOption", 10);
        this.addOutputInterface("Output");
        this.addOption("Operation", "SelectOption", {
            selected: "Add",
            items: [ "Add", "Subtract" ]
        });
    }

     calculate() {
        const n1 = this.getInterface("Number 1").value;
        const n2 = this.getInterface("Number 2").value;
        const operation = this.getOptionValue("Operation").selected;
        let result;
        if (operation === "Add") {
            result = n1 + n2;
        } else if (operation === "Subtract") {
            result = n1 - n2;
        }
        this.getInterface("Output").value = result;
    }

}

