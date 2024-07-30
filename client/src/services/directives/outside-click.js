const handlers = new WeakMap();

function onDocumentClick(e, el, fn) {
    let target = e.target;
    if (el !== target && !el.contains(target)) {
        fn(e);
    }
}

export default {
    bind(el, binding) {
        const fn = binding.value;
        const clickHandler = function (e) {
            onDocumentClick(e, el, fn);
        };

        document.addEventListener("click", clickHandler);
        document.addEventListener("touchstart", clickHandler);
        handlers.set(el, clickHandler);
    },
    unbind(el) {
        const handler = handlers.get(el);
        if (handler) {
            document.removeEventListener("click", handler);
            document.removeEventListener("touchstart", handler);
            handlers.delete(el);
        }
    },
};
