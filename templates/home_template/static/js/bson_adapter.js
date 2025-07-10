(function() {
    class ObjectId {
        constructor(value) {
            this.value = value;
        }

        toString() {
            return this.value;
        }

        static fromArgs(args) {
            return new ObjectId(args[0]);
        }
    }

    window.telepath.register('ObjectId', ObjectId);
})();
