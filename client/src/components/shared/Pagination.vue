<template>
  <div class="pagination">
    <div class="controls">
      <img
        class="arrow"
        :class="{ 'disabled-arrow': !collection.pagination.hasPrevPage }"
        src="@/assets/images/keyboard-arrow-left.svg"
        @click.stop.prevent="onLeftArrowClick"
      />
      <div
        v-for="n in collection.pagination.calcTotalPages(collection.pagination)"
        class="page"
        :class="{ 'current-page': collection.pagination.page === n }"
        :key="n"
        @click.stop.prevent="onPageClick(n)"
      >
        {{ n }}
      </div>
      <img
        class="arrow"
        :class="{ 'disabled-arrow': !collection.pagination.hasNextPage }"
        src="@/assets/images/keyboard-arrow-right.svg"
        @click.stop.prevent="onRightArrowClick"
      />
    </div>
    <div class="statistics">
      Showing {{ collection.pagination.currentPageStart }} -
      {{ collection.pagination.currentPageEnd }} of {{ collection.pagination.totalCount }}
      {{ model | pluralize(collection.pagination.totalCount) }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    // the collection to paginate
    collection: {
      required: true,
      type: Object,
    },
    // if a shallow clone of the collection should be used,
    // in order to newly leverage collection properties that may already
    // be tied to UI otherwise
    useCollectionClone: {
      type: Boolean,
      default: false,
    },
    // case-sensitive string of collection's model, in order to display pluralized
    model: {
      type: String,
      default: 'Opportunity',
    },
  },
  methods: {
    async onPageClick(pageNumber) {
      if (pageNumber !== this.collection.pagination.page) {
        this.$emit('start-loading')
        let c = this.useCollectionClone ? this.collection.shallowClone() : this.collection
        c.pagination.page = pageNumber
        c.refresh()
          .then(() => {
            this.collection.pagination = c.pagination
            this.collection.list = c.list
          })
          .finally(() => {
            this.$emit('end-loading')
          })
      }
    },
    onLeftArrowClick() {
      if (this.collection.pagination.hasPrevPage) {
        this.$emit('start-loading')
        // a clone is used here in order to leverage collection.refresh
        // without triggering any collection.refreshing -related renders.
        let c = this.useCollectionClone ? this.collection.shallowClone() : this.collection

        c.prevPage()
          .then(() => {
            this.collection.pagination = c.pagination
            this.collection.list = c.list
          })
          .finally(() => {
            this.$emit('end-loading')
          })
      }
    },
    onRightArrowClick() {
      if (this.collection.pagination.hasNextPage) {
        this.$emit('start-loading')
        // a clone is used here in order to leverage collection.refresh
        // without triggering any collection.refreshing -related renders.
        let c = this.useCollectionClone ? this.collection.shallowClone() : this.collection

        c.nextPage()
          .then(() => {
            this.collection.pagination = c.pagination
            this.collection.list = c.list
          })
          .finally(() => {
            this.$emit('end-loading')
          })
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';

.pagination {
  display: flex;
  flex-flow: row;
  align-items: center;
  font-size: 0.875rem;
  flex-wrap: wrap;
}

.controls {
  display: flex;
  flex-flow: row;
  align-items: center;
}

.arrow,
.page {
  @include pointer-on-hover;
  opacity: 0.4;
  &:hover {
    opacity: 1;
  }
}

.disabled-arrow {
  &:hover {
    cursor: not-allowed;
    opacity: 0.4;
  }
}

.page {
  margin: 0 0.25rem;
}

.current-page {
  color: $dark-green;
  opacity: 1;
  &:hover {
    cursor: default;
  }
}

.statistics {
  margin-left: auto;
  opacity: 0.4;
}
</style>
