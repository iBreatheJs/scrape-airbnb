import { Table, TableData, TableOptions } from "./tstable/table";
import { fetchEzy } from "./utils";
console.log("airbnb")

export interface Dictionary<TValue> {
    [id: string]: TValue;
}

window.addEventListener('DOMContentLoaded', function () {
    let updateBtn = document.getElementById("update")
    if (updateBtn) {
        updateBtn.addEventListener("click", () => {
            console.log("btn")
            fetchEzy<TableData>('/scrape').then(res => {
                console.log("data updated!!!")
            })
        });
    } else {
        alert("err")
    }
})

getTable()

export function getTable() {
    getData().then(data => {
        // process data in place
        constructTable(data)
    })
};

function getData() {
    return fetchEzy<TableData>('/rooms/all').then(res => {
        // return fetchEzy<TableData>('/scrape').then(res => {
        console.log("aRes")
        console.log(res)

        // TODO: only EUR, no leverage atm, implement some type of switch between quote currencies to draw the different tables
        // or maybe it should be part of it / passed to the table and afterwards be filtered in some data processing func, thats the nicest probably 
        // let data = {
        //   tables: aRes.data.tables,
        //   tradesByPair: aRes.data.tradesByPair
        // }
        return res
    })
}

function constructTable(data: TableData) {

    var header = {
        'id': 'id',
        'price': 'price',
        'title': 'title',
        'link': 'link',
    }



    let options: TableOptions<TableData> = {
        // rowFunc: rowFuncInnerTable, // defined below
        sortable: {
            all: true
        },
        alternateColour: false,
        // editable: onEdit // defined below
    }

    let tableHtml = document.getElementById("table") as HTMLTableElement;



    // nested table, instantiated for each asset listing the trades of the asset
    let table = new Table(tableHtml, header, data, options)
    // table.options.editable = true
    // table.options.filterBox = true
    table.options.filter = {}
    // table.options.filter.filterConfig = filter_config
    // table.options.filter.filterConfig = TRANSACTION_TYPE
    table.options.search = true

    table.drawTable()

}
