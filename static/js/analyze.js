// =========================================================
// QUEUEWISE
// ANALYZE PAGE - CLEAN FINAL VERSION
// =========================================================


// =========================================================
// ICONS
// =========================================================

const ICONS = {
    wait: `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M12 7v5l3 3"></path>
        </svg>
    `,

    cost: `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M9.5 15c0 1.2 1.1 2 2.5 2s2.5-.8 2.5-1.8c0-2.6-5-1.1-5-3.7 0-1 1.1-1.8 2.5-1.8s2.5.8 2.5 2"></path>
            <path d="M12 7v1"></path>
            <path d="M12 16v1"></path>
        </svg>
    `,

    check: `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M8 12.5l2.5 2.5L16 9.5"></path>
        </svg>
    `,

    warn: `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M12 4L2 20h20L12 4z"></path>
            <path d="M12 10.5v4"></path>
            <path d="M12 17h.01"></path>
        </svg>
    `,

    play: `
        <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 5v14l12-7z"></path>
        </svg>
    `,

    plus: `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
            <path d="M12 5v14"></path>
            <path d="M5 12h14"></path>
        </svg>
    `,

    robot: `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="4" y="9" width="16" height="11" rx="2"></rect>
            <path d="M9 13h.01"></path>
            <path d="M15 13h.01"></path>
            <path d="M12 5v4"></path>
            <path d="M9 5h6"></path>
        </svg>
    `,

    loader: `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
            <path d="M20 12a8 8 0 1 1-2.34-5.66"></path>
        </svg>
    `
};


function icon(name, extraClass = "") {
    return `
        <span class="icon ${extraClass}">
            ${ICONS[name] || ""}
        </span>
    `;
}


// =========================================================
// PAGE ELEMENTS
// =========================================================

const form = document.getElementById("analysis-form");

const submitButton =
    document.getElementById("submit-button");

const submitIcon =
    document.getElementById("submit-icon");

const submitLoader =
    document.getElementById("submit-loader");

const submitLabel =
    document.getElementById("submit-label");

const resetButton =
    document.getElementById("reset-form");

const analyzeDescriptionButton =
    document.getElementById(
        "analyze-description"
    );

const aiExtractionResult =
    document.getElementById(
        "ai-extraction-result"
    );


const statusBox =
    document.getElementById("status-box");

const resultsBox =
    document.getElementById("results-box");

const resultsBody =
    document.getElementById("results-body");

const rawJson =
    document.getElementById("raw-json");

const chartDiv =
    document.getElementById("cost-wait-chart");


const theoryBox =
    document.getElementById("theory-box");

const theoryBody =
    document.getElementById("theory-body");


// CURRENT CONDITION

const currentWait =
    document.getElementById("current-wait");

const currentUtil =
    document.getElementById("current-util");

const currentCost =
    document.getElementById("current-cost");

const currentStatus =
    document.getElementById("current-status");

const currentStatusDetail =
    document.getElementById("current-status-detail");


// RECOMMENDATION

const recommendationCard =
    document.getElementById("recommendation-card");

const recommendationTitle =
    document.getElementById("recommendation-title");

const recommendationReason =
    document.getElementById("recommendation-reason");

const recommendationTags =
    document.getElementById("recommendation-tags");

const recommendationBignums =
    document.getElementById("recommendation-bignums");

const recommendationDetails =
    document.getElementById("recommendation-details");

const recommendationDetailsText =
    document.getElementById("recommendation-details-text");

const alternativesBlock =
    document.getElementById("alternatives-block");

const alternativesList =
    document.getElementById("alternatives-list");

const indicatorBlock =
    document.getElementById("indicator-block");


// CUSTOM SCENARIOS

const customList =
    document.getElementById("custom-list");

const addCustomButton =
    document.getElementById("add-custom");


const MAX_CUSTOM = 5;

const customScenarios = [];

const numberFormat =
    new Intl.NumberFormat("id-ID");


// =========================================================
// BUSINESS CONTEXT
// Context only. No operational numbers are generated.
// =========================================================

const BUSINESS_CONTEXTS = {
    coffee: {
        name: "Coffee Shop",
        icon: "☕",
        description:
            "Queue at an ordering, cashier, or pickup point."
    },

    restaurant: {
        name: "Restaurant",
        icon: "🍽️",
        description:
            "Queue at an ordering, cashier, or service point."
    },

    campus: {
        name: "Campus Counter",
        icon: "🎓",
        description:
            "Student queue at a campus service counter."
    },

    clinic: {
        name: "Clinic",
        icon: "🏥",
        description:
            "Patient flow through a service point."
    },

    laundry: {
        name: "Laundry Service",
        icon: "🧺",
        description:
            "Customer drop-off, processing, or pickup queue."
    },

    retail: {
        name: "Small Retail",
        icon: "🛍️",
        description:
            "Checkout queue at a retail service point."
    }
};


let selectedBusiness = "";


const businessCards =
    document.querySelectorAll(".business-card");

const businessContext =
    document.getElementById("business-context");

const exampleIcon =
    document.getElementById("example-icon");

const exampleTitle =
    document.getElementById("example-title");

const exampleDescription =
    document.getElementById("example-description");


businessCards.forEach(function (card) {

    card.addEventListener(
        "click",
        function () {

            const key =
                card.dataset.business;

            const data =
                BUSINESS_CONTEXTS[key];


            if (!data) {
                return;
            }


            selectedBusiness =
                key;


            businessCards.forEach(
                function (item) {

                    item.classList.remove(
                        "is-selected"
                    );

                }
            );


            card.classList.add(
                "is-selected"
            );


            if (exampleIcon) {

                exampleIcon.textContent =
                    data.icon;

            }


            if (exampleTitle) {

                exampleTitle.textContent =
                    data.name;

            }


            if (exampleDescription) {

                exampleDescription.textContent =
                    data.description;

            }


            if (businessContext) {

                businessContext.hidden =
                    false;

            }

        }
    );

});


// =========================================================
// FORM HELPERS
// =========================================================

function getValue(name) {

    const element =
        form.elements[name];


    if (!element) {
        return "";
    }


    return element.value;

}


function getNumber(
    name,
    fallback = 0
) {

    const raw =
        getValue(name);


    if (
        raw === "" ||
        raw === null ||
        raw === undefined
    ) {

        return fallback;

    }


    const value =
        Number(raw);


    return Number.isFinite(value)
        ? value
        : fallback;

}


function readForm() {

    return {

        arrival_rate:
            getNumber("arrival_rate"),

        service_time:
            getNumber("service_time"),

        staff:
            getNumber("staff"),

        operating_hours:
            getNumber("operating_hours"),

        staff_cost:
            getNumber("staff_cost"),

        max_wait:
            getNumber("max_wait"),

        budget:
            getNumber("budget"),


        speedup_percent:
            getNumber(
                "speedup_percent",
                0
            ),

        speedup_cost:
            getNumber(
                "speedup_cost",
                0
            ),

        preorder_share_percent:
            getNumber(
                "preorder_share_percent",
                0
            ),

        preorder_cost:
            getNumber(
                "preorder_cost",
                0
            ),


        custom_scenarios:
            customScenarios,


        description:
            String(
                getValue("description") || ""
            ).trim(),


        source_type:
            getValue("source_type") ||
            "manual",

        source_reference:
            String(
                getValue("source_reference") || ""
            ).trim(),

        source_url:
            String(
                getValue("source_url") || ""
            ).trim(),


        business_type:
            selectedBusiness,


        replications:
            30

    };

}


// =========================================================
// STATUS / LOADING
// =========================================================

function hideStatus() {

    if (!statusBox) {
        return;
    }


    statusBox.hidden =
        true;

    statusBox.className =
        "status-box";

    statusBox.textContent =
        "";

}


function showStatus(
    message,
    type = "error"
) {

    if (!statusBox) {
        return;
    }


    statusBox.textContent =
        message;

    statusBox.className =
        "status-box status-" +
        type;

    statusBox.hidden =
        false;

}


function setLoading(
    isLoading
) {

    if (!submitButton) {
        return;
    }


    submitButton.disabled =
        isLoading;


    submitButton.classList.toggle(
        "is-loading",
        isLoading
    );


    if (submitLabel) {

       submitLabel.textContent =
    isLoading
        ? "QueueWise AI is analyzing..."
        : "Run AI Queue Analysis";
    }

}


// =========================================================
// FORMATTERS
// =========================================================

function money(value) {

    return (
        "Rp " +
        numberFormat.format(
            Math.round(
                Number(value) || 0
            )
        )
    );

}


function fmtStat(
    stat,
    decimals,
    suffix
) {

    if (!stat) {
        return "—";
    }


    const mean =
        Number(stat.mean);

    const halfWidth =
        Number(stat.half_width);


    if (
        !Number.isFinite(mean) ||
        !Number.isFinite(halfWidth)
    ) {

        return "—";

    }


    return (
        mean.toFixed(decimals) +
        suffix +
        " ± " +
        halfWidth.toFixed(decimals) +
        suffix
    );

}


function fmtPercentStat(
    stat,
    decimals
) {

    if (!stat) {
        return "—";
    }


    const meanValue =
        Number(stat.mean);

    const halfWidthValue =
        Number(stat.half_width);


    if (
        !Number.isFinite(meanValue) ||
        !Number.isFinite(halfWidthValue)
    ) {

        return "—";

    }


    const mean =
        (
            meanValue *
            100
        ).toFixed(decimals);


    const halfWidth =
        (
            halfWidthValue *
            100
        ).toFixed(decimals);


    return (
        mean +
        "% ± " +
        halfWidth +
        "%"
    );

}


function makeCell(
    text,
    className = ""
) {

    const cell =
        document.createElement(
            "td"
        );


    cell.textContent =
        text;


    if (className) {

        cell.className =
            className;

    }


    return cell;

}


// =========================================================
// CUSTOM SCENARIOS
// =========================================================

function describeSpec(spec) {

    const parts = [];


    if (
        spec.staff_change > 0
    ) {

        parts.push(
            "+" +
            spec.staff_change +
            " staff"
        );

    }


    if (
        spec.staff_change < 0
    ) {

        parts.push(
            spec.staff_change +
            " staff"
        );

    }


    if (
        spec.speedup_percent > 0
    ) {

        parts.push(
            "service -" +
            spec.speedup_percent +
            "%"
        );

    }


    if (
        spec.preorder_share_percent > 0
    ) {

        parts.push(
            spec.preorder_share_percent +
            "% pre-order"
        );

    }


    if (
        spec.extra_cost > 0
    ) {

        parts.push(
            "+" +
            money(
                spec.extra_cost
            ) +
            "/day"
        );

    }


    return parts.length
        ? parts.join(", ")
        : "no change";

}


function renderCustomList() {

    if (!customList) {
        return;
    }


    customList.replaceChildren();


    customScenarios.forEach(
        function (
            spec,
            index
        ) {

            const chip =
                document.createElement(
                    "span"
                );


            chip.className =
                "chip-item";


            const label =
                document.createElement(
                    "span"
                );


            label.textContent =
                spec.name +
                " (" +
                describeSpec(spec) +
                ")";


            const remove =
                document.createElement(
                    "button"
                );


            remove.type =
                "button";


            remove.className =
                "chip-remove";


            remove.setAttribute(
                "aria-label",
                "Remove scenario " +
                spec.name
            );


            remove.textContent =
                "×";


            remove.addEventListener(
                "click",
                function () {

                    customScenarios.splice(
                        index,
                        1
                    );


                    renderCustomList();

                }
            );


            chip.append(
                label,
                remove
            );


            customList.appendChild(
                chip
            );

        }
    );

}


function resetCustomInputs() {

    const customName =
        document.getElementById(
            "custom_name"
        );

    const customStaff =
        document.getElementById(
            "custom_staff"
        );

    const customSpeedup =
        document.getElementById(
            "custom_speedup"
        );

    const customPreorder =
        document.getElementById(
            "custom_preorder"
        );

    const customCost =
        document.getElementById(
            "custom_cost"
        );


    if (customName) {
        customName.value = "";
    }


    if (customStaff) {
        customStaff.value = 0;
    }


    if (customSpeedup) {
        customSpeedup.value = 0;
    }


    if (customPreorder) {
        customPreorder.value = 0;
    }


    if (customCost) {
        customCost.value = 0;
    }

}


if (addCustomButton) {

    addCustomButton.addEventListener(
        "click",
        function () {

            hideStatus();


            if (
                customScenarios.length >=
                MAX_CUSTOM
            ) {

                showStatus(
                    "You can add up to 5 custom scenarios."
                );

                return;

            }


            const nameInput =
                document.getElementById(
                    "custom_name"
                );

            const staffInput =
                document.getElementById(
                    "custom_staff"
                );

            const speedupInput =
                document.getElementById(
                    "custom_speedup"
                );

            const preorderInput =
                document.getElementById(
                    "custom_preorder"
                );

            const costInput =
                document.getElementById(
                    "custom_cost"
                );


            const spec = {

                name:
                    (
                        nameInput
                            ? nameInput.value.trim()
                            : ""
                    ) ||
                    "Custom " +
                    (
                        customScenarios.length +
                        1
                    ),


                staff_change:
                    Number(
                        staffInput
                            ? staffInput.value
                            : 0
                    ),


                speedup_percent:
                    Number(
                        speedupInput
                            ? speedupInput.value
                            : 0
                    ),


                preorder_share_percent:
                    Number(
                        preorderInput
                            ? preorderInput.value
                            : 0
                    ),


                extra_cost:
                    Number(
                        costInput
                            ? costInput.value
                            : 0
                    )

            };


            const hasChange =
                spec.staff_change !== 0 ||
                spec.speedup_percent !== 0 ||
                spec.preorder_share_percent !== 0 ||
                spec.extra_cost !== 0;


            if (!hasChange) {

                showStatus(
                    "Add at least one change before creating a custom scenario."
                );

                return;

            }


            customScenarios.push(
                spec
            );


            renderCustomList();

            resetCustomInputs();

        }
    );

}

// =========================================================
// AI STRATEGY EXPLORER
// =========================================================

function showAIStrategies(result) {


    const card =
        document.getElementById(
            "ai-strategy-card"
        );


    const list =
        document.getElementById(
            "ai-strategy-list"
        );


    if(
        !card ||
        !list
    ){
        return;
    }


   const strategies =
    result.strategy_ideas?.strategies ||
    result.agent?.strategy_ideas?.strategies;


    if(
        !Array.isArray(strategies) ||
        strategies.length === 0
    ){

        card.hidden = true;

        return;

    }



    list.innerHTML = "";



    strategies.forEach(
        function(strategy){


            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "ai-strategy-item";


            item.innerHTML = `

                <span class="ai-strategy-category">
                    ${strategy.category || "Strategy"}
                </span>


                <h4>
                    ${strategy.name}
                </h4>


                <p>
                    ${strategy.reason || ""}
                </p>

            `;


            list.appendChild(
                item
            );


        }
    );



    card.hidden = false;

}

// =========================================================
// CURRENT CONDITION
// =========================================================

function showCurrentCondition(
    result
) {

    if (
        !Array.isArray(
            result.scenarios
        ) ||
        result.scenarios.length === 0
    ) {

        return;

    }


    const baseline =
        result.scenarios[0];


    const metrics =
        baseline.metrics || {};


    const wait =
        Number(
            metrics.avg_wait?.mean
        );


    const utilization =
        Number(
            metrics.utilization?.mean
        );


    const cost =
        Number(
            baseline.cost?.total
        );


    const maxWait =
        Number(
            result.inputs?.max_wait
        );


    const withinBudget =
        Boolean(
            baseline.cost?.within_budget
        );


    const stable =
        Boolean(
            baseline.capacity?.is_stable
        );


    if (currentWait) {

        currentWait.textContent =
            Number.isFinite(wait)
                ? wait.toFixed(2)
                : "—";

    }


    if (currentUtil) {

        currentUtil.textContent =
            Number.isFinite(
                utilization
            )
                ? (
                    utilization *
                    100
                ).toFixed(1) +
                "%"
                : "—";

    }


    if (currentCost) {

        currentCost.textContent =
            Number.isFinite(cost)
                ? money(cost)
                : "—";

    }


    if (
        !currentStatus ||
        !currentStatusDetail
    ) {

        return;

    }


    currentStatus.className =
        "summary-status";


    if (!stable) {

        currentStatus.textContent =
            "Unstable";


        currentStatus.classList.add(
            "status-text-bad"
        );


        currentStatusDetail.textContent =
            "Demand exceeds service capacity.";


        return;

    }


    const meetsWait =
        Number.isFinite(wait) &&
        Number.isFinite(maxWait) &&
        wait <= maxWait;


    if (
        meetsWait &&
        withinBudget
    ) {

        currentStatus.textContent =
            "Meets targets";


        currentStatus.classList.add(
            "status-text-good"
        );


        currentStatusDetail.textContent =
            "Current system satisfies both criteria.";

    } else if (
        !meetsWait &&
        !withinBudget
    ) {

        currentStatus.textContent =
            "Needs improvement";


        currentStatus.classList.add(
            "status-text-bad"
        );


        currentStatusDetail.textContent =
            "Wait target and budget are both missed.";

    } else if (
        !meetsWait
    ) {

        currentStatus.textContent =
            "Wait too high";


        currentStatus.classList.add(
            "status-text-warn"
        );


        currentStatusDetail.textContent =
            "Current average wait exceeds your target.";

    } else {

        currentStatus.textContent =
            "Over budget";


        currentStatus.classList.add(
            "status-text-warn"
        );


        currentStatusDetail.textContent =
            "Current system exceeds your daily budget.";

    }

}


// =========================================================
// RESULTS TABLE
// =========================================================

function showTable(
    result
) {

    if (!resultsBody) {
        return;
    }


    resultsBody.replaceChildren();


    const recommendedId =
        result.recommendation
            ?.evaluation
            ?.id ?? null;


    result.scenarios.forEach(
        function (
            scenario,
            index
        ) {

            const metrics =
                scenario.metrics || {};


            const row =
                document.createElement(
                    "tr"
                );


            row.className =
                "result-row";


            if (index === 0) {

                row.classList.add(
                    "baseline-row"
                );

            }


            if (
                recommendedId !== null &&
                scenario.id ===
                recommendedId
            ) {

                row.classList.add(
                    "recommended-row"
                );

            }


            const nameCell =
                makeCell(
                    scenario.name ||
                    "Unnamed scenario",
                    "scenario-name"
                );


            if (index === 0) {

                const currentTag =
                    document.createElement(
                        "span"
                    );


                currentTag.className =
                    "tag tag-neutral";


                currentTag.textContent =
                    "current";


                nameCell.appendChild(
                    currentTag
                );

            }


            if (
                recommendedId !== null &&
                scenario.id ===
                recommendedId
            ) {

                const recommendedTag =
                    document.createElement(
                        "span"
                    );


                recommendedTag.className =
                    "tag tag-ok";


                recommendedTag.textContent =
                    "recommended";


                nameCell.appendChild(
                    recommendedTag
                );

            }


            if (
                scenario.capacity &&
                !scenario.capacity.is_stable
            ) {

                const unstableTag =
                    document.createElement(
                        "span"
                    );


                unstableTag.className =
                    "tag tag-warn";


                unstableTag.textContent =
                    "unstable";


                nameCell.appendChild(
                    unstableTag
                );

            }


            row.appendChild(
                nameCell
            );


            row.appendChild(
                makeCell(
                    String(
                        scenario
                            .effective
                            ?.staff ??
                        "—"
                    )
                )
            );


            row.appendChild(
                makeCell(
                    fmtStat(
                        metrics.avg_wait,
                        2,
                        " min"
                    )
                )
            );


            row.appendChild(
                makeCell(
                    fmtPercentStat(
                        metrics.utilization,
                        1
                    )
                )
            );


            row.appendChild(
                makeCell(
                    fmtStat(
                        metrics
                            .throughput_per_hour,
                        1,
                        ""
                    )
                )
            );


            row.appendChild(
                makeCell(
                    fmtStat(
                        metrics
                            .overtime_minutes,
                        1,
                        " min"
                    )
                )
            );


            row.appendChild(
                makeCell(
                    money(
                        scenario
                            .cost
                            ?.total
                    )
                )
            );


            const withinBudget =
                Boolean(
                    scenario
                        .cost
                        ?.within_budget
                );


            const budgetCell =
                makeCell(
                    "",
                    withinBudget
                        ? "budget-yes"
                        : "budget-no"
                );


            budgetCell.innerHTML =
                icon(
                    withinBudget
                        ? "check"
                        : "warn"
                ) +
                (
                    withinBudget
                        ? " Within budget"
                        : " Over budget"
                );


            row.appendChild(
                budgetCell
            );


            resultsBody.appendChild(
                row
            );

        }
    );

}


// =========================================================
// THEORY VALIDATION
// =========================================================

function showTheory(
    theoryChecks
) {

    if (
        !theoryBox ||
        !theoryBody
    ) {

        return;

    }


    theoryBody.replaceChildren();


    if (
        !Array.isArray(
            theoryChecks
        ) ||
        theoryChecks.length === 0
    ) {

        theoryBox.hidden =
            true;


        return;

    }


    theoryChecks.forEach(
        function (item) {

            const row =
                document.createElement(
                    "tr"
                );


            row.appendChild(
                makeCell(
                    item.scenario ||
                    "—"
                )
            );


            row.appendChild(
                makeCell(
                    Number.isFinite(
                        Number(
                            item.theory_wait
                        )
                    )
                        ? Number(
                            item.theory_wait
                        ).toFixed(3) +
                        " min"
                        : "—"
                )
            );


            row.appendChild(
                makeCell(
                    Number.isFinite(
                        Number(
                            item.simulated_wait
                        )
                    ) &&
                    Number.isFinite(
                        Number(
                            item.half_width
                        )
                    )
                        ? Number(
                            item.simulated_wait
                        ).toFixed(3) +
                        " ± " +
                        Number(
                            item.half_width
                        ).toFixed(3) +
                        " min"
                        : "—"
                )
            );


            row.appendChild(
                makeCell(
                    Number.isFinite(
                        Number(
                            item.error_percent
                        )
                    )
                        ? Number(
                            item.error_percent
                        ).toFixed(1) +
                        "%"
                        : "—"
                )
            );


            const within =
                Boolean(
                    item.within_tolerance
                );


            const statusCell =
                makeCell(
                    "",
                    within
                        ? "budget-yes"
                        : "budget-no"
                );


            statusCell.innerHTML =
                icon(
                    within
                        ? "check"
                        : "warn"
                ) +
                (
                    within
                        ? " Yes"
                        : " No"
                );


            row.appendChild(
                statusCell
            );


            theoryBody.appendChild(
                row
            );

        }
    );


    theoryBox.hidden =
        false;

}


// =========================================================
// RECOMMENDATION
// =========================================================

function splitReason(text) {

    if (!text) {

        return {
            short: "",
            rest: ""
        };

    }


    const match =
        text.match(
            /^(.+?[.!?])(?:\s+|$)([\s\S]*)$/
        );


    if (!match) {

        return {
            short: text,
            rest: ""
        };

    }


    return {

        short:
            match[1],

        rest:
            match[2].trim()

    };

}


function arrowIcon() {

    return `
        <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.4"
        >
            <path d="M5 12h13"></path>
            <path d="M13 6l6 6-6 6"></path>
        </svg>
    `;

}

// =========================================================
// AI STRATEGY EXPLORER
// =========================================================
    function showAIStrategies(result) {

    console.log(
        "STRATEGY CHECK:",
        result.strategy_ideas,
        result.agent?.strategy_ideas
    );

    const card =
        document.getElementById(
            "ai-strategy-card"
        );

    const list =
        document.getElementById(
            "ai-strategy-list"
        );


    if (
        !card ||
        !list
    ) {
        return;
    }


    const strategies =
    result.strategy_ideas?.strategies ||
    result.agent?.strategy_ideas?.strategies;


    if (
        !Array.isArray(strategies) ||
        strategies.length === 0
    ) {

        card.hidden = true;
        return;

    }


    list.innerHTML = "";


    strategies.forEach(
        function(strategy) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "ai-strategy-item";


            item.innerHTML = `

                <div class="ai-strategy-category">
                    ${
                        strategy.category ||
                        "AI Strategy"
                    }
                </div>


                <h4>
                    ${
                        strategy.name ||
                        "Unnamed strategy"
                    }
                </h4>


                <p>
                    ${
                        strategy.reason ||
                        ""
                    }
                </p>

            `;


            list.appendChild(
                item
            );

        }
    );


    card.hidden = false;

}

function showRecommendation(
    result
) {

    if (
        !recommendationCard
    ) {

        return;

    }


    const recommendation =
        result.recommendation;


    if (
        !recommendation ||
        !recommendation.evaluation
    ) {

        recommendationCard.hidden =
            true;


        return;

    }


    const chosen =
        recommendation.evaluation;


    const table =
        Array.isArray(
            recommendation.table
        )
            ? recommendation.table
            : [];


    const baseline =
        table.length
            ? table[0]
            : chosen;


    if (
        recommendationTitle
    ) {

        recommendationTitle.textContent =
            recommendation.recommended_name ||
            "Recommended scenario";

    }


    if (
        recommendationBignums
    ) {

        recommendationBignums.replaceChildren();


        const waitBox =
            document.createElement(
                "div"
            );


        waitBox.className =
            "bignum";


        const chosenWait =
            Number(
                chosen.avg_wait
            );


        const baselineWait =
            Number(
                baseline.avg_wait
            );


        if (
            chosen.id ===
            baseline.id
        ) {

            waitBox.innerHTML = `
                <span class="bignum-label">
                    ${icon("wait")}
                    Average wait
                </span>

                <div class="bignum-value">

                    <span class="bignum-new">
                        ${
                            Number.isFinite(
                                chosenWait
                            )
                                ? chosenWait.toFixed(
                                    2
                                )
                                : "—"
                        }
                    </span>

                    <span class="unit">
                        min
                    </span>

                </div>
            `;

        } else {

            const improved =
                Number.isFinite(
                    chosenWait
                ) &&
                Number.isFinite(
                    baselineWait
                ) &&
                chosenWait <
                baselineWait;


            waitBox.innerHTML = `
                <span class="bignum-label">
                    ${icon("wait")}
                    Average wait
                </span>

                <div class="bignum-value">

                    <span class="bignum-old">
                        ${
                            Number.isFinite(
                                baselineWait
                            )
                                ? baselineWait.toFixed(
                                    2
                                )
                                : "—"
                        }
                    </span>

                    <span
                        class="bignum-arrow ${
                            improved
                                ? "arrow-good"
                                : "arrow-bad"
                        }"
                    >
                        ${arrowIcon()}
                    </span>

                    <span
                        class="bignum-new ${
                            improved
                                ? "good"
                                : "bad"
                        }"
                    >
                        ${
                            Number.isFinite(
                                chosenWait
                            )
                                ? chosenWait.toFixed(
                                    2
                                )
                                : "—"
                        }
                    </span>

                    <span class="unit">
                        min
                    </span>

                </div>
            `;

        }


        recommendationBignums.appendChild(
            waitBox
        );


        const costBox =
            document.createElement(
                "div"
            );


        costBox.className =
            "bignum";


        costBox.innerHTML = `
            <span class="bignum-label">
                ${icon("cost")}
                Cost / day
            </span>

            <div class="bignum-value">

                <span class="bignum-new">
                    ${money(chosen.cost)}
                </span>

            </div>
        `;


        recommendationBignums.appendChild(
            costBox
        );

    }


    const reason =
        splitReason(
            recommendation.reason ||
            ""
        );


    if (
        recommendationReason
    ) {

        recommendationReason.textContent =
            reason.short;

    }


    if (
        recommendationDetails &&
        recommendationDetailsText
    ) {

        if (reason.rest) {

            recommendationDetails.hidden =
                false;


            recommendationDetailsText.textContent =
                reason.rest;

        } else {

            recommendationDetails.hidden =
                true;


            recommendationDetailsText.textContent =
                "";

        }

    }


    if (
        recommendationTags
    ) {

        recommendationTags.replaceChildren();


        function addTag(
            text,
            type
        ) {

            const element =
                document.createElement(
                    "span"
                );


            element.className =
                "rec-tag rec-tag-" +
                type;


            element.innerHTML =
                icon(
                    type === "ok"
                        ? "check"
                        : "warn"
                ) +
                " " +
                text;


            recommendationTags.appendChild(
                element
            );

        }


        if (
            recommendation.status ===
            "no_feasible_option"
        ) {

            addTag(
                "No scenario meets every criterion",
                "warn"
            );

        } else {

            addTag(
                chosen.meets_wait_target
                    ? "Meets wait target"
                    : "Misses wait target",

                chosen.meets_wait_target
                    ? "ok"
                    : "warn"
            );


            addTag(
                chosen.within_budget
                    ? "Within budget"
                    : "Over budget",

                chosen.within_budget
                    ? "ok"
                    : "warn"
            );


            if (
                chosen.uses_assumptions
            ) {

                addTag(
                    "Uses your assumptions",
                    "warn"
                );

            }

        }

    }


    if (
        alternativesList &&
        alternativesBlock
    ) {

        alternativesList.replaceChildren();


        const alternatives =
            Array.isArray(
                recommendation.alternatives
            )
                ? recommendation.alternatives
                : [];


        if (
            !alternatives.length
        ) {

            alternativesBlock.hidden =
                true;

        } else {

            alternativesBlock.hidden =
                false;


            alternatives.forEach(
                function (
                    alternative
                ) {

                    const item =
                        document.createElement(
                            "li"
                        );


                    item.textContent =
                        (
                            alternative.name ||
                            "Alternative"
                        ) +
                        ": " +
                        (
                            alternative.note ||
                            ""
                        );


                    alternativesList.appendChild(
                        item
                    );

                }
            );

        }

    }


    recommendationCard.hidden =
        false;

}


// =========================================================
// CRITERIA METERS
// =========================================================

function makeMeter(
    label,
    valueText,
    fraction,
    type,
    interpretation
) {

    const element =
        document.createElement(
            "div"
        );


    element.className =
        "meter";


    const safeFraction =
        Number.isFinite(
            fraction
        )
            ? fraction
            : 1;


    const width =
        Math.min(
            100,
            Math.max(
                0,
                safeFraction *
                100
            )
        );


    element.innerHTML = `

        <div class="meter-row">

            <span class="meter-label">
                ${label}
            </span>

            <strong class="meter-value">
                ${valueText}
            </strong>

        </div>


        <div class="meter-track">

            <div
                class="meter-fill meter-${type}"
                style="width: ${width}%"
            ></div>

        </div>


        <p class="meter-interpretation">
            ${interpretation}
        </p>

    `;


    return element;

}


function showIndicators(
    result
) {

    if (
        !indicatorBlock
    ) {

        return;

    }


    const recommendation =
        result.recommendation;


    if (
        !recommendation ||
        !recommendation.evaluation
    ) {

        return;

    }


    const chosen =
        recommendation.evaluation;


    const maxWait =
        Number(
            result.inputs
                ?.max_wait
        );


    const budget =
        Number(
            result.inputs
                ?.budget
        );


    const chosenWait =
        Number(
            chosen.avg_wait
        );


    const chosenCost =
        Number(
            chosen.cost
        );


    indicatorBlock.replaceChildren();


    const waitFraction =
        maxWait > 0 &&
        Number.isFinite(
            chosenWait
        )
            ? chosenWait /
            maxWait
            : 1;


    const waitDifference =
        Number.isFinite(
            chosenWait
        ) &&
        Number.isFinite(
            maxWait
        )
            ? Math.abs(
                maxWait -
                chosenWait
            )
            : 0;


    const waitInterpretation =
        chosen.meets_wait_target
            ? (
                "Average wait is " +
                waitDifference.toFixed(
                    2
                ) +
                " minutes below your target."
            )
            : (
                "Average wait is " +
                waitDifference.toFixed(
                    2
                ) +
                " minutes above your target."
            );


    indicatorBlock.appendChild(

        makeMeter(

            icon("wait") +
            " Waiting-time target",

            (
                Number.isFinite(
                    chosenWait
                )
                    ? chosenWait.toFixed(
                        2
                    )
                    : "—"
            ) +
            " / " +
            (
                Number.isFinite(
                    maxWait
                )
                    ? maxWait.toFixed(
                        2
                    )
                    : "—"
            ) +
            " min",

            waitFraction,

            chosen.meets_wait_target
                ? "ok"
                : "warn",

            waitInterpretation

        )

    );


    const budgetFraction =
        budget > 0 &&
        Number.isFinite(
            chosenCost
        )
            ? chosenCost /
            budget
            : 1;


    const budgetDifference =
        Number.isFinite(
            chosenCost
        ) &&
        Number.isFinite(
            budget
        )
            ? Math.abs(
                budget -
                chosenCost
            )
            : 0;


    const budgetInterpretation =
        chosen.within_budget
            ? (
                "Estimated cost is " +
                money(
                    budgetDifference
                ) +
                " below your daily budget."
            )
            : (
                "Estimated cost is " +
                money(
                    budgetDifference
                ) +
                " above your daily budget."
            );


    indicatorBlock.appendChild(

        makeMeter(

            icon("cost") +
            " Daily budget",

            money(
                chosenCost
            ) +
            " / " +
            money(
                budget
            ),

            budgetFraction,

            chosen.within_budget
                ? "ok"
                : "warn",

            budgetInterpretation

        )

    );

}


// =========================================================
// CHART
// =========================================================

function showChart(
    result
) {

    if (!chartDiv) {
        return;
    }


    if (
        typeof Plotly ===
        "undefined"
    ) {

        chartDiv.innerHTML = `
            <p class="chart-error">
                The chart library could not be loaded.
            </p>
        `;


        return;

    }


    const scenarios =
        result.scenarios;


    const maxWait =
        Number(
            result.inputs
                ?.max_wait
        );


    const budget =
        Number(
            result.inputs
                ?.budget
        );


    const xValues =
        scenarios.map(
            function (
                scenario
            ) {

                return (
                    Number(
                        scenario
                            .metrics
                            ?.avg_wait
                            ?.mean
                    ) ||
                    0
                );

            }
        );


    const xErrors =
        scenarios.map(
            function (
                scenario
            ) {

                return (
                    Number(
                        scenario
                            .metrics
                            ?.avg_wait
                            ?.half_width
                    ) ||
                    0
                );

            }
        );


    const yValues =
        scenarios.map(
            function (
                scenario
            ) {

                return (
                    Number(
                        scenario
                            .cost
                            ?.total
                    ) ||
                    0
                );

            }
        );


    const feasible =
        scenarios.map(
            function (
                scenario
            ) {

                const wait =
                    Number(
                        scenario
                            .metrics
                            ?.avg_wait
                            ?.mean
                    ) ||
                    0;


                return (
                    wait <= maxWait &&
                    Boolean(
                        scenario
                            .cost
                            ?.within_budget
                    )
                );

            }
        );


    const trace = {

        x:
            xValues,

        y:
            yValues,


        error_x: {

            type:
                "data",

            array:
                xErrors,

            color:
                "#94a3b8",

            thickness:
                1,

            width:
                3

        },


        text:
            scenarios.map(
                function (
                    scenario
                ) {

                    return (
                        scenario.name
                    );

                }
            ),


        mode:
            "markers+text",

        type:
            "scatter",

        textposition:
            "top center",


        textfont: {

            color:
                "#475569",

            size:
                11

        },


        marker: {

            size:
                14,

            color:
                feasible.map(
                    function (ok) {

                        return ok
                            ? "#22c55e"
                            : "#ef4444";

                    }
                ),

            line: {

                color:
                    "#ffffff",

                width:
                    2

            }

        },


        hovertemplate:
            "%{text}" +
            "<br>Wait: %{x:.2f} min" +
            "<br>Cost: %{y:,.0f}" +
            "<extra></extra>"

    };


    const maxY =
        Math.max(
            Number.isFinite(
                budget
            )
                ? budget *
                1.2
                : 0,

            ...yValues,

            1
        );


    const maxX =
        Math.max(
            Number.isFinite(
                maxWait
            )
                ? maxWait *
                1.8
                : 0,

            ...xValues.map(
                function (
                    value,
                    index
                ) {

                    return (
                        value +
                        xErrors[index]
                    );

                }
            ),

            1
        );


    const shapes = [];


    if (
        Number.isFinite(
            maxWait
        ) &&
        Number.isFinite(
            budget
        )
    ) {

        shapes.push(

            {
                type:
                    "rect",

                x0:
                    0,

                x1:
                    maxWait,

                y0:
                    0,

                y1:
                    budget,

                fillcolor:
                    "rgba(34, 197, 94, 0.08)",

                line: {
                    width:
                        0
                }
            },


            {
                type:
                    "line",

                x0:
                    maxWait,

                x1:
                    maxWait,

                y0:
                    0,

                y1:
                    maxY,

                line: {

                    color:
                        "#94a3b8",

                    dash:
                        "dash",

                    width:
                        1

                }
            },


            {
                type:
                    "line",

                x0:
                    0,

                x1:
                    maxX,

                y0:
                    budget,

                y1:
                    budget,

                line: {

                    color:
                        "#94a3b8",

                    dash:
                        "dash",

                    width:
                        1

                }
            }

        );

    }


    const layout = {

        paper_bgcolor:
            "rgba(0,0,0,0)",

        plot_bgcolor:
            "rgba(0,0,0,0)",


        font: {

            color:
                "#475569",

            family:
                "Inter, Arial, sans-serif"

        },


        margin: {

            l:
                70,

            r:
                25,

            t:
                40,

            b:
                60

        },


        xaxis: {

            title:
                "Average wait (minutes)",

            range:
                [
                    0,
                    maxX
                ],

            gridcolor:
                "rgba(100,116,139,0.12)",

            linecolor:
                "#e2e8f0",

            zeroline:
                false

        },


        yaxis: {

            title:
                "Cost per day",

            range:
                [
                    0,
                    maxY
                ],

            gridcolor:
                "rgba(100,116,139,0.12)",

            linecolor:
                "#e2e8f0",

            zeroline:
                false

        },


        shapes:
            shapes,


        showlegend:
            false

    };


    Plotly.newPlot(

        chartDiv,

        [
            trace
        ],

        layout,

        {
            displayModeBar:
                false,

            responsive:
                true
        }

    );

}

// =========================================================
// AI DESCRIPTION EXTRACTION
// =========================================================

const AI_EXTRACT_FIELDS = [
    "arrival_rate",
    "service_time",
    "staff",
    "operating_hours",
    "staff_cost",
    "max_wait",
    "budget"
];


const AI_FIELD_LABELS = {
    arrival_rate:
        "Customer arrival rate",

    service_time:
        "Average service time",

    staff:
        "Current staff / counters",

    operating_hours:
        "Operating hours",

    staff_cost:
        "Staff cost",

    max_wait:
        "Maximum acceptable wait",

    budget:
        "Maximum daily budget"
};


// ---------------------------------------------------------
// If AI detects business type and user has not selected one,
// select the matching business context.
// ---------------------------------------------------------

function applyAIBusinessType(
    extracted
) {

    const businessType =
        String(
            extracted?.business_type || ""
        ).trim();


    if (
        !businessType ||
        selectedBusiness
    ) {
        return;
    }


    const data =
        BUSINESS_CONTEXTS[
            businessType
        ];


    if (!data) {
        return;
    }


    selectedBusiness =
        businessType;


    businessCards.forEach(
        function (card) {

            const isMatch =
                card.dataset.business ===
                businessType;


            card.classList.toggle(
                "is-selected",
                isMatch
            );

        }
    );


    if (exampleIcon) {
        exampleIcon.textContent =
            data.icon;
    }


    if (exampleTitle) {
        exampleTitle.textContent =
            data.name;
    }


    if (exampleDescription) {
        exampleDescription.textContent =
            data.description;
    }


    if (businessContext) {
        businessContext.hidden =
            false;
    }

}


// ---------------------------------------------------------
// Fill only EMPTY fields.
// Manual values entered by the user always win.
// ---------------------------------------------------------

function applyExtractedData(
    extracted
) {

    const filled = [];
    const preserved = [];


    AI_EXTRACT_FIELDS.forEach(
        function (fieldName) {

            const field =
                form.elements[
                    fieldName
                ];


            if (!field) {
                return;
            }


            const value =
                extracted?.[
                    fieldName
                ];


            if (
                value === null ||
                value === undefined ||
                value === ""
            ) {
                return;
            }


            const currentValue =
                String(
                    field.value || ""
                ).trim();


            // Do not overwrite a value
            // already entered by the user.
            if (currentValue !== "") {

                preserved.push(
                    fieldName
                );

                return;
            }


            field.value =
                value;


            filled.push(
                fieldName
            );

        }
    );


    return {
        filled:
            filled,

        preserved:
            preserved
    };

}


// ---------------------------------------------------------
// Convert AI note / ambiguity safely to readable text.
// ---------------------------------------------------------

function agentMessageText(
    item
) {

    if (
        typeof item ===
        "string"
    ) {
        return item;
    }


    if (
        item &&
        typeof item ===
        "object"
    ) {

        return (
            item.message ||
            item.reason ||
            item.note ||
            JSON.stringify(item)
        );

    }


    return String(
        item ?? ""
    );

}


// ---------------------------------------------------------
// Show extraction summary below the AI description.
// ---------------------------------------------------------

function renderAIExtraction(
    extracted,
    applied
) {

    if (!aiExtractionResult) {
        return;
    }


    aiExtractionResult.replaceChildren();


    const detected =
        AI_EXTRACT_FIELDS.filter(
            function (fieldName) {

                const value =
                    extracted?.[
                        fieldName
                    ];


                return (
                    value !== null &&
                    value !== undefined &&
                    value !== ""
                );

            }
        );


    const missing =
        AI_EXTRACT_FIELDS.filter(
            function (fieldName) {

                const value =
                    extracted?.[
                        fieldName
                    ];


                return (
                    value === null ||
                    value === undefined ||
                    value === ""
                );

            }
        );


    const header =
        document.createElement(
            "strong"
        );


    header.textContent =
        "✓ QueueWise AI understood your description";


    aiExtractionResult.appendChild(
        header
    );


    const summary =
        document.createElement(
            "p"
        );


    summary.textContent =
        "Detected " +
        detected.length +
        " of " +
        AI_EXTRACT_FIELDS.length +
        " required values.";


    aiExtractionResult.appendChild(
        summary
    );


    // Show values detected by AI.

    if (detected.length) {

        const list =
            document.createElement(
                "ul"
            );


        detected.forEach(
            function (fieldName) {

                const item =
                    document.createElement(
                        "li"
                    );


                item.textContent =
                    AI_FIELD_LABELS[
                        fieldName
                    ] +
                    ": " +
                    extracted[
                        fieldName
                    ];


                list.appendChild(
                    item
                );

            }
        );


        aiExtractionResult.appendChild(
            list
        );

    }


    // Tell user which fields still need manual input.

    if (missing.length) {

        const missingText =
            document.createElement(
                "p"
            );


        missingText.textContent =
            "Still needed: " +
            missing
                .map(
                    function (fieldName) {

                        return (
                            AI_FIELD_LABELS[
                                fieldName
                            ]
                        );

                    }
                )
                .join(", ") +
            ".";


        aiExtractionResult.appendChild(
            missingText
        );

    } else {

        const complete =
            document.createElement(
                "p"
            );


        complete.textContent =
            "✓ All required values were detected. Review the fields below before running the simulation.";


        aiExtractionResult.appendChild(
            complete
        );

    }


    // Manual values that were intentionally preserved.

    if (
        applied &&
        applied.preserved &&
        applied.preserved.length
    ) {

        const preservedText =
            document.createElement(
                "p"
            );


        preservedText.textContent =
            "Existing manual values were kept and were not overwritten by AI.";


        aiExtractionResult.appendChild(
            preservedText
        );

    }


    // Ambiguities from Gemini.

    const ambiguities =
        Array.isArray(
            extracted?.ambiguities
        )
            ? extracted.ambiguities
            : [];


    if (ambiguities.length) {

        const title =
            document.createElement(
                "strong"
            );


        title.textContent =
            "Needs clarification:";


        aiExtractionResult.appendChild(
            title
        );


        const list =
            document.createElement(
                "ul"
            );


        ambiguities.forEach(
            function (ambiguity) {

                const item =
                    document.createElement(
                        "li"
                    );


                item.textContent =
                    agentMessageText(
                        ambiguity
                    );


                list.appendChild(
                    item
                );

            }
        );


        aiExtractionResult.appendChild(
            list
        );

    }


    // Additional AI notes.

    const notes =
        Array.isArray(
            extracted?.notes
        )
            ? extracted.notes
            : [];


    if (notes.length) {

        const title =
            document.createElement(
                "strong"
            );


        title.textContent =
            "Notes:";


        aiExtractionResult.appendChild(
            title
        );


        const list =
            document.createElement(
                "ul"
            );


        notes.forEach(
            function (note) {

                const item =
                    document.createElement(
                        "li"
                    );


                item.textContent =
                    agentMessageText(
                        note
                    );


                list.appendChild(
                    item
                );

            }
        );


        aiExtractionResult.appendChild(
            list
        );

    }


    aiExtractionResult.hidden =
        false;

}


// =========================================================
// AI DESCRIPTION BUTTON
// =========================================================

if (
    analyzeDescriptionButton
) {

    analyzeDescriptionButton.addEventListener(
        "click",

        async function () {

            hideStatus();


            const description =
                String(
                    getValue(
                        "description"
                    ) || ""
                ).trim();


            if (!description) {

                showStatus(
                    "Describe your queue first so QueueWise AI has something to understand.",
                    "error"
                );

                return;

            }


            const originalText =
                analyzeDescriptionButton
                    .textContent;


            analyzeDescriptionButton.disabled =
                true;


            analyzeDescriptionButton.textContent =
                "Understanding your queue...";


            try {

                const response =
                    await fetch(
                        "/api/agent/extract",
                        {

                            method:
                                "POST",

                            headers: {

                                "Content-Type":
                                    "application/json"

                            },

                            body:
                                JSON.stringify(
                                    {

                                        description:
                                            description,

                                        business_type:
                                            selectedBusiness

                                    }
                                )

                        }
                    );


                const rawResponse =
                    await response.text();


                let result;


                try {

                    result =
                        rawResponse
                            ? JSON.parse(
                                rawResponse
                            )
                            : {};

                } catch (
                    jsonError
                ) {

                    console.error(
                        "Invalid AI response:",
                        rawResponse
                    );


                    throw new Error(
                        "QueueWise AI returned an invalid response."
                    );

                }


                if (!response.ok) {

                    throw new Error(
                        result.error ||
                        result.message ||
                        "QueueWise AI could not understand the description."
                    );

                }


                const extracted =
                    result.extracted ||
                    {};


                // Business context detected by AI.
                applyAIBusinessType(
                    extracted
                );


                // Fill only empty operational fields.
                const applied =
                    applyExtractedData(
                        extracted
                    );


                renderAIExtraction(
                    extracted,
                    applied
                );

                renderAIReviewCard(
    extracted
);


                showStatus(
                    "QueueWise AI understood your description. Review the detected values below.",
                    "success"
                );


            } catch (
                error
            ) {

                console.error(
                    "QueueWise AI extraction error:",
                    error
                );


                showStatus(
                    error.message,
                    "error"
                );


            } finally {

                analyzeDescriptionButton.disabled =
                    false;


                analyzeDescriptionButton.textContent =
                    originalText;

            }

        }
    );

}   

// =========================================================
// AI REVIEW CARD
// =========================================================

function renderAIReviewCard(
    extracted
) {

    const card =
        document.getElementById(
            "ai-review-card"
        );


    const list =
        document.getElementById(
            "ai-review-list"
        );


    if (!card || !list) {
        return;
    }


    list.innerHTML = "";


    const fields = [
        {
            key: "arrival_rate",
            label: "Customer arrival rate",
            unit: "customers/hour"
        },

        {
            key: "service_time",
            label: "Average service time",
            unit: "minutes/customer"
        },

        {
            key: "staff",
            label: "Active staff",
            unit: "people"
        },

        {
            key: "operating_hours",
            label: "Operating hours",
            unit: "hours/day"
        },

        {
            key: "staff_cost",
            label: "Staff cost",
            unit: "Rp/hour"
        },

        {
            key: "max_wait",
            label: "Maximum waiting target",
            unit: "minutes"
        },

        {
            key: "budget",
            label: "Daily budget",
            unit: "Rp/day"
        }
    ];


    fields.forEach(
        function(item){

            const value =
                extracted?.[
                    item.key
                ];


            if (
                value === null ||
                value === undefined ||
                value === ""
            ) {
                return;
            }


            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "ai-review-item";


            row.innerHTML = `

                <div class="ai-review-item-left">

                    <span class="ai-review-item-label">
                        ${item.label}
                    </span>

                    <span class="ai-review-item-source">
                        ✨ AI detected
                    </span>

                </div>


                <strong class="ai-review-item-value">
                    ${value}
                    <small>
                        ${item.unit}
                    </small>
                </strong>

            `;


            list.appendChild(
                row
            );

        }
    );


    card.hidden = false;

}

// =========================================================
// INPUT VALIDATION
// =========================================================

function validateInputData() {

    const data =
        readForm();


    if (
        data.arrival_rate <= 0
    ) {

        return (
            "Customer arrival rate must be greater than 0."
        );

    }


    if (
        data.service_time <= 0
    ) {

        return (
            "Average service time must be greater than 0."
        );

    }


    if (
        data.staff < 1
    ) {

        return (
            "At least one active staff member or counter is required."
        );

    }


    if (
        data.operating_hours <= 0
    ) {

        return (
            "Operating hours must be greater than 0."
        );

    }


    if (
        data.max_wait <= 0
    ) {

        return (
            "Maximum acceptable wait must be greater than 0."
        );

    }


    if (
        data.staff_cost < 0 ||
        data.budget < 0
    ) {

        return (
            "Cost and budget values cannot be negative."
        );

    }


    return "";

}


// =========================================================
// SUBMIT ANALYSIS
// =========================================================

if (form) {

    form.addEventListener(
        "submit",
        async function (
            event
        ) {

            event.preventDefault();


            hideStatus();


            if (
                !form.checkValidity()
            ) {

                form.reportValidity();

                return;

            }


            const validationMessage =
                validateInputData();


            if (
                validationMessage
            ) {

                showStatus(
                    validationMessage,
                    "error"
                );

                return;

            }


            if (
                resultsBox
            ) {

                resultsBox.hidden =
                    true;

            }


            setLoading(
                true
            );


            try {

                const payload =
                    readForm();


                console.log(
                    "QueueWise payload:",
                    payload
                );


                let response;


                try {

                  response =
    await fetch(
        "/api/agent/analyze",
        {

                                method:
                                    "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify(
                                        payload
                                    )

                            }
                        );

                } catch (
                    networkError
                ) {

                    console.error(
                        "Network error:",
                        networkError
                    );


                    showStatus(
                        "Cannot connect to the QueueWise server. Make sure Flask is running.",
                        "error"
                    );


                    return;

                }


                const rawResponse =
                    await response.text();


                console.log(
                    "QueueWise raw response:",
                    rawResponse
                );


                let result;


                try {

                    result =
                        rawResponse
                            ? JSON.parse(
                                rawResponse
                            )
                            : {};

                } catch (
                    jsonError
                ) {

                    console.error(
                        "Invalid JSON response:",
                        jsonError
                    );


                    console.error(
                        "Server returned:",
                        rawResponse
                    );


                    showStatus(
                        "The server returned an invalid response (HTTP " +
                        response.status +
                        "). Check the Flask terminal for the actual error.",
                        "error"
                    );


                    return;

                }


                console.log(
                    "QueueWise parsed result:",
                    result
                );


                if (
                    !response.ok
                ) {

                    const errorMessage =
                        result.error ||
                        result.message ||
                        (
                            "Server error (HTTP " +
                            response.status +
                            ")."
                        );


                    console.error(
                        "QueueWise API error:",
                        result
                    );


                    showStatus(
                        errorMessage,
                        "error"
                    );


                    return;

                }


                if (
                    !result ||
                    !Array.isArray(
                        result.scenarios
                    )
                ) {

                    console.error(
                        "Unexpected API response:",
                        result
                    );


                    showStatus(
                        "Analysis completed, but the server response does not contain scenario results.",
                        "error"
                    );


                    return;

                }


                if (
                    result.scenarios.length ===
                    0
                ) {

                    showStatus(
                        "The analysis returned no scenarios to compare.",
                        "error"
                    );


                    return;

                }


                try {

                    showAIStrategies(
                        result
);

                    showCurrentCondition(
                        result
                    );


                    showRecommendation(
                        result
                    );


                    showIndicators(
                        result
                    );


                    showTable(
                        result
                    );


                    showTheory(
                        result.theory_validation ||
                        []
                    );


                    showChart(
                        result
                    );

                } catch (
                    renderError
                ) {

                    console.error(
                        "Result rendering error:",
                        renderError
                    );


                    console.error(
                        "Result that caused the error:",
                        result
                    );


                    if (
                        rawJson
                    ) {

                        rawJson.textContent =
                            JSON.stringify(
                                result,
                                null,
                                2
                            );

                    }


                    if (
                        resultsBox
                    ) {

                        resultsBox.hidden =
                            false;

                    }


                    showStatus(
                        "The analysis was completed by the server, but the result display failed: " +
                        renderError.message,
                        "error"
                    );


                    return;

                }


                if (
                    rawJson
                ) {

                    rawJson.textContent =
                        JSON.stringify(
                            result,
                            null,
                            2
                        );

                }


                if (
                    resultsBox
                ) {

                    resultsBox.hidden =
                        false;


                    resultsBox.scrollIntoView(
                        {

                            behavior:
                                "smooth",

                            block:
                                "start"

                        }
                    );

                }

            } catch (
                unexpectedError
            ) {

                console.error(
                    "Unexpected QueueWise error:",
                    unexpectedError
                );


                showStatus(
                    "Unexpected error: " +
                    unexpectedError.message,
                    "error"
                );

            } finally {

                setLoading(
                    false
                );

            }

        }
    );

}


// =========================================================
// RESET FORM
// =========================================================

if (
    resetButton &&
    form
) {

    resetButton.addEventListener(
        "click",
        function () {

            form.reset();


            selectedBusiness =
                "";


            businessCards.forEach(
                function (
                    card
                ) {

                    card.classList.remove(
                        "is-selected"
                    );

                }
            );


            if (
                businessContext
            ) {

                businessContext.hidden =
                    true;

            }


            customScenarios.splice(
                0,
                customScenarios.length
            );


            renderCustomList();


            hideStatus();


            if (
                resultsBox
            ) {

                resultsBox.hidden =
                    true;

            }


            if (
                recommendationCard
            ) {

                recommendationCard.hidden =
                    true;

            }


            if (
                theoryBox
            ) {

                theoryBox.hidden =
                    true;

            }


            document
                .querySelectorAll(
                    ".field-help, .advanced-panel, .optional-panel"
                )
                .forEach(
                    function (
                        details
                    ) {

                        details.open =
                            false;

                    }
                );


            if (
                typeof Plotly !==
                "undefined" &&
                chartDiv
            ) {

                try {

                    Plotly.purge(
                        chartDiv
                    );

                } catch (
                    error
                ) {

                    console.debug(
                        error
                    );

                }

            }


            form.scrollIntoView(
                {

                    behavior:
                        "smooth",

                    block:
                        "start"

                }
            );

        }
    );

}


// =========================================================
// HELP POPOVERS
// =========================================================

const helpDetails =
    document.querySelectorAll(
        ".field-help"
    );


helpDetails.forEach(
    function (
        details
    ) {

        details.addEventListener(
            "toggle",
            function () {

                if (
                    !details.open
                ) {

                    return;

                }


                helpDetails.forEach(
                    function (
                        other
                    ) {

                        if (
                            other !==
                            details
                        ) {

                            other.open =
                                false;

                        }

                    }
                );

            }
        );

    }
);


document.addEventListener(
    "click",
    function (
        event
    ) {

        if (
            event.target.closest(
                ".field-help"
            )
        ) {

            return;

        }


        helpDetails.forEach(
            function (
                details
            ) {

                details.open =
                    false;

            }
        );

    }
);


// =========================================================
// INITIAL ICONS
// =========================================================

if (
    submitIcon
) {

    submitIcon.innerHTML =
        ICONS.play;

}


if (
    submitLoader
) {

    submitLoader.innerHTML =
        ICONS.loader;

}


const addIcon =
    document.getElementById(
        "add-icon"
    );


if (
    addIcon
) {

    addIcon.innerHTML =
        ICONS.plus;

}


const recommendationIcon =
    document.getElementById(
        "rec-label-icon"
    );


if (
    recommendationIcon
) {

    recommendationIcon.innerHTML =
        ICONS.robot;

}