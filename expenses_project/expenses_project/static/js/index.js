function getExpenseObj(id) {
    fetch("/expenses/edit-expenses/"+id, {
        method : 'GET',
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById("modal-amount").value = result.amount;
        document.getElementById("modal-date").value = result.date;
        document.getElementById("modal-description").value = result.description;
        const categoryID = "modal-category-" + result.category;
        document.getElementById(categoryID).checked = true;
        document.getElementById("edit-expenses-form").action = `/expenses/edit-expenses/${id}`
    
    })
}

function deleteExpenseObj(id) {
    document.getElementById("delete-expenses-form").action = `/expenses/delete-expenses/${id}`
}