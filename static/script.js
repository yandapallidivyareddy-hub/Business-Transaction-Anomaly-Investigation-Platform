
// ============================================================
// FIN-41 BUSINESS TRANSACTION ANOMALY INVESTIGATION PLATFORM
// Frontend JavaScript
// ============================================================


document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeTransactionSearch();

        initializeInvestigationForms();

        initializeButtons();

    }
);


// ============================================================
// TRANSACTION SEARCH
// ============================================================

function initializeTransactionSearch() {

    const searchBox =
        document.getElementById(
            "transactionSearch"
        );

    const table =
        document.getElementById(
            "transactionsTable"
        );


    // If the current page does not contain
    // the transaction table, do nothing.

    if (!searchBox || !table) {

        return;

    }


    searchBox.addEventListener(
        "input",
        function () {

            const searchValue =
                searchBox.value
                    .toLowerCase()
                    .trim();


            const rows =
                table.querySelectorAll(
                    "tbody tr"
                );


            rows.forEach(
                function (row) {

                    const rowText =
                        row.textContent
                            .toLowerCase();


                    if (
                        rowText.includes(
                            searchValue
                        )
                    ) {

                        row.style.display =
                            "";

                    }

                    else {

                        row.style.display =
                            "none";

                    }

                }
            );

        }
    );

}


// ============================================================
// INVESTIGATION FORM HANDLING
// ============================================================

function initializeInvestigationForms() {

    const forms =
        document.querySelectorAll(
            "form"
        );


    forms.forEach(
        function (form) {

            form.addEventListener(
                "submit",
                function (event) {

                    const requiredFields =
                        form.querySelectorAll(
                            "[required]"
                        );


                    let valid = true;


                    requiredFields.forEach(
                        function (field) {

                            if (
                                !field.value.trim()
                            ) {

                                valid = false;

                                field.classList.add(
                                    "input-error"
                                );

                            }

                            else {

                                field.classList.remove(
                                    "input-error"
                                );

                            }

                        }
                    );


                    if (!valid) {

                        event.preventDefault();

                        showMessage(
                            "Please complete all required fields.",
                            "error"
                        );

                    }

                }
            );

        }
    );

}


// ============================================================
// BUTTON INITIALIZATION
// ============================================================

function initializeButtons() {

    const createButtons =
        document.querySelectorAll(
            ".investigate-button"
        );


    createButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    button.classList.add(
                        "button-loading"
                    );

                }
            );

        }
    );

}


// ============================================================
// INVESTIGATION CONFIRMATION
// ============================================================

function confirmInvestigation() {

    return window.confirm(
        "Are you sure you want to create an investigation for this transaction?"
    );

}


// ============================================================
// DELETE / REMOVE CONFIRMATION
// ============================================================

function confirmAction(
    message
) {

    if (!message) {

        message =
            "Are you sure you want to continue?";

    }


    return window.confirm(
        message
    );

}


// ============================================================
// SAVE INVESTIGATION MESSAGE
// ============================================================

function showSavedMessage() {

    showMessage(
        "Investigation saved successfully.",
        "success"
    );

}


// ============================================================
// GENERAL MESSAGE DISPLAY
// ============================================================

function showMessage(
    message,
    type = "info"
) {

    const existingMessage =
        document.querySelector(
            ".js-message"
        );


    if (existingMessage) {

        existingMessage.remove();

    }


    const messageBox =
        document.createElement(
            "div"
        );


    messageBox.className =
        "js-message " +
        "js-message-" +
        type;


    messageBox.textContent =
        message;


    document.body.prepend(
        messageBox
    );


    setTimeout(
        function () {

            messageBox.remove();

        },
        4000
    );

}


// ============================================================
// TEXTAREA CHARACTER COUNTER
// ============================================================

function initializeCharacterCounter(
    textareaId,
    counterId,
    maxLength
) {

    const textarea =
        document.getElementById(
            textareaId
        );

    const counter =
        document.getElementById(
            counterId
        );


    if (!textarea || !counter) {

        return;

    }


    textarea.addEventListener(
        "input",
        function () {

            const length =
                textarea.value.length;


            counter.textContent =
                length +
                " / " +
                maxLength;


            if (
                length > maxLength
            ) {

                counter.classList.add(
                    "counter-error"
                );

            }

            else {

                counter.classList.remove(
                    "counter-error"
                );

            }

        }
    );

}


// ============================================================
// AUTO-HIDE TEMPORARY MESSAGES
// ============================================================

function autoHideMessages() {

    const messages =
        document.querySelectorAll(
            ".temporary-message"
        );


    messages.forEach(
        function (message) {

            setTimeout(
                function () {

                    message.style.opacity =
                        "0";


                    setTimeout(
                        function () {

                            message.remove();

                        },
                        500
                    );

                },
                4000
            );

        }
    );

}


// ============================================================
// TABLE ROW HIGHLIGHT
// ============================================================

function initializeTableHighlight() {

    const rows =
        document.querySelectorAll(
            "#transactionsTable tbody tr"
        );


    rows.forEach(
        function (row) {

            row.addEventListener(
                "click",
                function () {

                    rows.forEach(
                        function (otherRow) {

                            otherRow.classList.remove(
                                "selected-row"
                            );

                        }
                    );


                    row.classList.add(
                        "selected-row"
                    );

                }
            );

        }
    );

}


// ============================================================
// NUMBER FORMATTING
// ============================================================

function formatAmount(
    amount
) {

    const number =
        Number(amount);


    if (
        Number.isNaN(number)
    ) {

        return amount;

    }


    return number.toLocaleString(
        "en-IN"
    );

}


// ============================================================
// SAFE TEXT HANDLING
// ============================================================

function escapeHTML(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value;


    return div.innerHTML;

}


// ============================================================
// CONSOLE STATUS
// ============================================================

console.log(
    "FIN-41 Investigation Platform JavaScript loaded."
);

