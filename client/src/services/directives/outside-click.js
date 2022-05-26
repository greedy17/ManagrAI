let instances = [];

function onDocumentClick(e, el, fn) {
    let target = e.target;
    if (el !== target && !el.contains(target)) {
        fn(e);
    }
}

export default {
    bind(el, binding) {
        el.dataset.outsideClickIndex = instances.length;

        const fn = binding.value;
        const click = function (e) {
            onDocumentClick(e, el, fn);
        };

        document.addEventListener("click", click);
        document.addEventListener("touchstart", click);
        instances.push(click);
    },
    unbind(el) {
        const click = function (e) {
            onDocumentClick(e, el, fn);
        };
        const index = el.dataset.outsideClickIndex;
        const handler = instances[index];
        document.removeEventListener("click", handler);
        document.removeEventListener("touchstart", click);
        instances.splice(index, 1);
    },
};