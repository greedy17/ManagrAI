<template>
  <div class="main-content">
    <div class="top-section">
      <span>Results: {{filteredArticles.length}}</span>
      <div class="display-flex">
        <div class="summary-button">
          <img src="@/assets/images/add.svg" /><span>Add Column</span>
        </div>
        <div class="summary-button">
          <img src="@/assets/images/file-excel.svg" /><span>Export</span>
        </div>
      </div>
    </div>
    <div class="table">
      <div>
        <div class="table-header">
          <div class="table-cell">Name</div>
          <div class="table-cell">Source</div>
          <div class="table-cell">Date</div>
          <div class="table-cell">Author</div>
          <div class="table-cell">Sentiment</div>
          <div class="table-cell">Key Messages</div>
        </div>
      </div>
      <div v-for="(article, i) in filteredArticles" :key="i" class="table-row" @click="selectArticle(article)">
        <div class="table-cell table-cell-name">{{ article.title }}</div>
        <div class="table-cell">{{ article.source }}</div>
        <div class="table-cell">Today</div>
        <div class="table-cell">{{ article.author }}</div>
        <div class="table-cell">Positive</div>
        <div class="table-cell">Tesla revolutionizes the automotive industry...</div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'ClipReportsMainContent',
  components: {

  },
  data() {
    return {
      articles: [],
      filteredArticles: [],
    }
  },
  watch: {

  },
  created() {
    
  },
  methods: {
    selectArticle(article) {
      this.$store.dispatch('updateSelectedArticle', article)
    },
  },
  computed: {
    
  }
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
  .main-content {
    // display: flex;
    background-color: $white;
    border-radius: 8px;
    margin: 1rem 0.5rem 0.5rem 0;
    padding: 1rem;
    min-height: 88vh;
    color: $dark-black-blue;
    width: 65vw;
  }
  .display-flex {
    display: flex;
  }
  .space-between {
    display: flex;
    justify-content: space-between;
  }
  .table {
    font-size: 12px;
  }
  .table-cell {
    text-overflow: ellipsis;
    width: 10vw;
    overflow-x: hidden;
    white-space: nowrap;
    // padding: 0 0.2rem;
    padding: 0.5rem;
  }
  .table-cell-name {
    color: $dark-green;
    background-color: $soft-gray;
    border-radius: 4px;
  }
  .table-header {
    display: flex;
    border: 1px solid $soft-gray;
    background-color: $soft-gray;
    padding: 0.5rem;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
  }
  .table-row {
    display: flex;
    border: 1px solid $soft-gray;
    background-color: $white;
    padding: 0.5rem;
  }
  .summary-button {
    @include gray-text-button();
    margin: 0 0.5rem;
    // padding: 8px 16px;
    img {
      height: 12px;
      margin-right: 0.5rem;
    }
  }
  .top-section {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
  }
</style>