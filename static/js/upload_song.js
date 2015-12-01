console.log("yo");

function validateForm() {
    var x = document.forms["upload"]["file"].value;
    console.log("Ayy"+x);
    if (x === null || x === "") {
    	console.log("Empty..");
    	document.getElementById("message-alert").style.display = "block";
       	document.getElementById("message").innerHTML = "<strong>Warning!</strong>  You must select a file";
        return false;
    }
}