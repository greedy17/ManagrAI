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
    this.getArticles()
  },
  methods: {
    getArticles() {
      const res = [
        {
          icon: 'https://www.vectorlogo.zone/logos/marketwatch/marketwatch-icon.svg',
          source: 'MarketWatch',
          title: 'EV stocks see green after Tesla, Rivian, Nio report upbeat deliveries data',
          preview: `Electric-vehicle maker stocks got a broad boost Monday, after upbeat delivery and production data from a host of companies in the U.S. and...`,
          coverPhoto: `https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/New_York_City_%28New_York%2C_USA%29%2C_Empire_State_Building_--_2012_--_6448.jpg/1200px-New_York_City_%28New_York%2C_USA%29%2C_Empire_State_Building_--_2012_--_6448.jpg`,
          time: '5 mins ago',
          author: 'Eric Peters',
          link: 'https://www.nyan.cat/',
          data: {},
        },
        {
          icon: 'https://www.vectorlogo.zone/logos/marketwatch/marketwatch-icon.svg',
          source: 'Automotive News',
          title: 'Tesla deliveries in China surge as supply-chain concerns ease.',
          preview: `Electric-vehicle maker stocks got a broad boost Monday, after upbeat delivery and production data from a host of companies in the U.S. and...`,
          coverPhoto: `https://empire-s3-production.bobvila.com/articles/wp-content/uploads/2023/01/iStock-1372085619-hidden-costs-of-owning-an-electric-car-vehicle-charging-by-solar-panels.jpg`,
          time: '10 mins ago',
          author: 'Susan Miller',
          link: 'https://www.nyan.cat/',
          data: {},
        },
        {
          icon: 'https://www.vectorlogo.zone/logos/marketwatch/marketwatch-icon.svg',
          source: 'MotorTrend',
          title: '2025 Tesla Model S: What you should know',
          preview: `Electric-vehicle maker stocks got a broad boost Monday, after upbeat delivery and production data from a host of companies in the U.S. and...`,
          coverPhoto: `https://hips.hearstapps.com/hmg-prod/images/2022-tesla-model-s-mmp-3-1628540852.png?crop=0.891996891996892xw:1xh;center,top&resize=1200:*`,
          time: '1 hr ago',
          author: 'Rachel Myers',
          link: 'https://www.nyan.cat/',
          data: {},
        },
      ]
      this.articles = res
      this.filteredArticles = res
    },
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