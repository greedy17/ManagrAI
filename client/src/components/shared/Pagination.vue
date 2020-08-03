<template>
  <div class="pagination">
    <div class="controls">
      <img
        class="arrow"
        src="@/assets/images/keyboard-arrow-left.svg"
        @click.prevent="onLeftArrowClick"
      />
      <div class="pages">
        <span
          v-for="n in collection.pagination.calcTotalPages(collection.pagination)"
          class="page"
          :class="{ current: collection.pagination.page === n }"
          :key="n"
          @click.prevent="onPageClick(n)"
        >
          {{ n }}
        </span>
      </div>
      <img
        class="arrow"
        src="@/assets/images/keyboard-arrow-right.svg"
        @click.prevent="onRightArrowClick"
      />
    </div>
    <div class="statistics">
      Showing {{ collection.pagination.currentPageStart }} -
      {{ collection.pagination.currentPageEnd }} of {{ collection.pagination.totalCount }}
      {{ 'Opportunity' | pluralize(collection.pagination.totalCount) }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    collection: {
      required: true,
      type: Object,
    },
  },
  methods: {
    appendToCollection() {
      this.collection.addNextPage()
    },
    onPageClick(pageNumber) {
      if (pageNumber !== this.collection.pagination.page) {
        this.collection.pagination.page = pageNumber
        this.collection.refresh()
      }
    },
    onLeftArrowClick() {
      if (this.collection.pagination.hasPrevPage) {
        this.collection.prevPage()
      }
    },
    onRightArrowClick() {
      if (this.collection.pagination.hasNextPage) {
        this.collection.nextPage()
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
}

.controls {
  display: flex;
  flex-flow: row;
  align-items: center;
}

.pages {
  margin: 0 0.5rem;
}

.arrow,
.page {
  @include pointer-on-hover;
  opacity: 0.4;
  &:hover {
    opacity: 1;
  }
}

.page {
  margin: 0 0.25rem;
}

.current {
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
