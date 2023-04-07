class DataSourceNode extends BaklavaJS.Core.Node {

    type = "data_source";
    name = "Data";

    constructor() {
        super();
        this.addOutputInterface("Output");
        this.addOption("Select Dataset", "SelectOption", {
            // Query dataset list
            items: [ "" ]
        });
    }

}

