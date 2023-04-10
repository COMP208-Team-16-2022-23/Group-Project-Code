class DisplayNode extends BaklavaJS.Core.Node {

    type = "DisplayNode";
    name = "Display";

    constructor() {
        super();
        this.addInputInterface("Input");
        this.addOption("Text", "TextOption");
    }

    calculate() {
        let text = this.getInterface("Input").value;
        this.setOptionValue("Text", text);
    }

}

class EndNode extends BaklavaJS.Core.Node {

    type = "EndNode";
    name = "End Process";

    constructor() {
        super();
        this.addInputInterface("End Process");
    }

    calculate() {
    }

}

