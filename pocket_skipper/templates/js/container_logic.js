var storage_key_name = "third";
var mapping = new Map();
var current_containers = ["unsorted"];
var drake;

function container_setup() {
    console.log("Setting up dragula.");
    drake = dragula([document.getElementById("items")]);

    load_containers();
    for (var [key, value] of mapping.entries()) {
        if (current_containers.indexOf(key) == -1){
            new_div = create_container(key);

            for (var i of value) {
                new_div.appendChild(document.getElementById("div_" + i));
            }
        }
    }
}

function page_exit(e){
    save_containers();
}

function add_container() {
    var name = prompt("Enter name of new container.");
    create_container(name);
}

function rename_or_delete(event) {
    var new_name = prompt("Please enter new name. Leave empty to delete and move everything to " +
        "unsorted.", "Rename or delete.");

    if (new_name) {
        fs_name = event.srcElement.parentElement.id.split("_")[0];
        items = mapping.get(fs_name);
        mapping.set(new_name, items);
        mapping.delete(fs_name);

        event.srcElement.innerText = new_name;
        event.srcElement.parentElement.id = new_name + "_fieldset";
    }
    else {
        unsorted_div = $("#items")[0];
        $(event.srcElement).parent().find(".item").each(function(i, item){
            num = item.id.substr(4);
            unsorted_div.appendChild(document.getElementById("div_" + num));
        });

        $(event.srcElement).parent().remove()
    }

}

function create_container(name) {
    var fieldset = document.createElement("fieldset");

    var legend = document.createElement("legend");
    legend.innerHTML = name;
    fieldset.appendChild(legend);
    fieldset.id = name + "_fieldset";
    fieldset.onclick = rename_or_delete;

    var d = document.createElement("div");
    d.id = name + "_div";

    var d2 = document.createElement("div");
    d2.innerHTML = "initial";
    d.appendChild(d2);

    fieldset.appendChild(d);

    $(fieldset).insertBefore("#unsorted_container");
    drake.containers.push(document.getElementById(d.id));

    return d;
}

function save_containers(){
    console.log("Saving...");
    mapping = new Map();

    $("fieldset").each(function(i, fieldset) {
        fs_name = fieldset.id.split("_")[0];
        items = [];
        $(fieldset).find(".mark_as_read_span").each(function(i, item) {
            items.push(item.id);
        });

        mapping.set(fs_name, items);
    });

    serialized = JSON.stringify(Array.from(mapping.entries()));
    localStorage.setItem(storage_key_name, serialized);
}

function load_containers() {
    console.log("Loading...");

    serialized = localStorage.getItem(storage_key_name);
    mapping = new Map(JSON.parse(serialized));
}

