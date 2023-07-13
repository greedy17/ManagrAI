<template>
  <div class="main-content">
    <div class="left-content">
      <div>
        <div class="gray-background">
          <div class="toggle-container" :class="summaryChat === 'SUMMARY' ? 'active' : ''" @click="changeSummaryChat('SUMMARY')">
            <p>Summary</p>
          </div>
          <div class="toggle-container" :class="summaryChat === 'CHAT' ? 'active' : ''" @click="changeSummaryChat('CHAT')">
            <p>Chat</p>
          </div>
        </div>
        <div v-if="summaryChat === 'SUMMARY'">
          <p class="small-title-text"><img src="@/assets/images/sparkles-nofill-round.svg" />Summary</p>
        </div>
        <div v-else>
          <p class="small-title-text"><img src="@/assets/images/sparkles-nofill-round.svg" />Chat</p>
        </div>
      </div>
      <div v-if="summaryChat === 'SUMMARY'">
        <div v-if="!summary" class="summary-buttons-container">
          <button class="summary-button wide" @click="generateSummary"><img src="@/assets/images/sparkles-round.svg" />Generate Summary</button>
        </div>
        <div v-else>
          <div class="highlights-summary-container">
            <div>
              <h3 class="highlights">Highlights:</h3>
              <div v-for="(highlight, i) in summary.highlights" :key="i">
                <div class="display-flex">
                  <span class="divier-dot large-dot">.</span>
                  <span>{{ highlight }}</span>
                </div>
              </div>
            </div>
            <div>
              <h3>Overall Summary:</h3>
              <div>{{ summary.overview }}</div>
            </div>
          </div>
          <div class="summary-buttons-container">
            <button class="summary-button"><img src="@/assets/images/sparkles-round.svg" />Regenerate</button>
            <button class="summary-button dark-button"><img src="@/assets/images/sparkles-round.svg" />New Summary</button>
          </div>
        </div>
      </div>
    </div>
    <div class="right-content">
      <div class="updated-time">
        <span>Updated {{ getUpdated }} ago</span>
      </div>
      <div class="search-results">
        <div>
          <p>Results: {{ filteredArticles.length }}</p>
        </div>
        <div class="search-bar">
          <img class="search" src="@/assets/images/search-round.svg" />
          <input
            @input="searchTitles"
            type="search"
            :placeholder="`Search`"
            v-model="filterText"
          />
        </div>
      </div>
      <div class="card-container">
        <div v-for="article in filteredArticles" :key="article.id" class="card">
          <div class="display-flex">
            <div class="">
              <div class="card-top-left">
                <img :src="article.icon" />
                <span>{{ article.source }}</span>
              </div>
              <h3 class="article-title" @click="goToArticle(article.link)">{{ article.title }}</h3>
              <h4 class="article-preview">{{ article.preview }}</h4>
            </div>
            <div @click="goToArticle(article.link)">
              <img :src="article.coverPhoto" class="cover-photo" />
            </div>
          </div>
          <div class="card-footer">
            <div class="author-time">
              <span>{{ article.time }}</span>
              <span class="divier-dot">.</span>
              <span>{{ article.author }}</span>
            </div>
            <div class="footer-icon-container">
              <img src="@/assets/images/sparkles-nofill-round.svg" class="footer-icon" />
              <img src="@/assets/images/tags.svg" class="footer-icon" />
              <img src="@/assets/images/search-round.svg" class="footer-icon" />
              <img src="@/assets/images/arrow-small-right.svg" class="right-arrow-footer" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  name: 'SummariesMainContent',
  components: {

  },
  data() {
    return {
      summary: null,
      articles: [],
      summaryChat: 'SUMMARY',
      filterText: '',
    }
  },
  watch: {

  },
  created() {
    this.getArticles()
  },
  methods: {
    changeSummaryChat(type) {
      this.summaryChat = type
    },
    async generateSummary() {
      const res = {
        overview: `Today's news highlights the success and growth of Tesla in Q2. The company achieved record deliveries in China, driven by tax credits and wider adoption. Tesla's Q2 results were impressive, with production and deliveries exceeding expectations. Additionally, plans for a new Tesla dealership in Orlando reflect the company's expanding local presence. These positive developments have fueled a 7% increase in Tesla's share prices.`,
        highlights: [
          'Telsa and BYD achieved record-high deliveries of their China-made cehicles in Q2',
          `Tesla's Q2 deliveries rose 83% compared to the previous year, driven by tax credits and broader adoption.`,
          `Tesla reported strong Q2 results, producing 479,700 cars and delivering 466,140 vehicles.`,
          `Plans were filed for a new Tesla dealership in Orlando as the company expands its local presence.`,
          `Tesla's quarterly deliveries beat expectations, resulting in a 7% jump in share prices.`,
        ]
      }
      this.summary = res
    },
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
          link: 'https://www.nyan.cat/'
        },
        {
          icon: 'https://www.vectorlogo.zone/logos/marketwatch/marketwatch-icon.svg',
          source: 'Automotive News',
          title: 'Tesla deliveries in China surge as supply-chain concerns ease.',
          preview: `Electric-vehicle maker stocks got a broad boost Monday, after upbeat delivery and production data from a host of companies in the U.S. and...`,
          coverPhoto: `https://empire-s3-production.bobvila.com/articles/wp-content/uploads/2023/01/iStock-1372085619-hidden-costs-of-owning-an-electric-car-vehicle-charging-by-solar-panels.jpg`,
          time: '10 mins ago',
          author: 'Susan Miller',
          link: 'https://www.nyan.cat/'
        },
        {
          icon: 'https://www.vectorlogo.zone/logos/marketwatch/marketwatch-icon.svg',
          source: 'MotorTrend',
          title: '2025 Tesla Model S: What you should know',
          preview: `Electric-vehicle maker stocks got a broad boost Monday, after upbeat delivery and production data from a host of companies in the U.S. and...`,
          coverPhoto: `https://hips.hearstapps.com/hmg-prod/images/2022-tesla-model-s-mmp-3-1628540852.png?crop=0.891996891996892xw:1xh;center,top&resize=1200:*`,
          time: '1 hr ago',
          author: 'Rachel Myers',
          link: 'https://www.nyan.cat/'
        },
      ]
      this.articles = res
      this.filteredArticles = res
    },
    goToArticle(link) {
      window.location.href = link
    },
    searchTitles() {
      console.log('this.filterText', this.filterText)
      this.filteredArticles = this.articles.filter(article => article.title.includes(this.filterText))
    },
  },
  computed: {
    getUpdated() {
      return '22 mins'
    }
  }
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
  .main-content {
    display: flex;
    background-color: $white;
    border-radius: 8px;
    margin-top: 1rem;
    padding: 1rem;
    min-height: 90vh;
    color: $dark-black-blue;
  }
  .display-flex {
    display: flex;
  }
  .space-between {
    display: flex;
    justify-content: space-between;
  }
  .search-results {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-left: 1rem;
    margin-right: 1rem;
    padding-left: 1rem;
  }
  .left-content {
    width: 25vw;
  }
  .right-content {
    width: 35vw;
  }
  .card-container {
    border-left: 1px solid $soft-gray;
    margin-left: 1rem;
    padding-left: 1rem;
    height: 75vh;
    overflow-y: auto;
  }
  .card {
    border: 1px solid $soft-gray;
    border-radius: 8px;
    box-shadow: 2px 2px 5px 0 $soft-gray;
    transition: all 0.3s;
    margin-bottom: 1rem;
    margin-right: 1rem;
  }
  .card:hover {
    transform: scale(1.025);
    box-shadow: 4px 4px 5px 0px $soft-gray;
  }
  .card-top-left {
    display: flex;
    font-size: 12px;
    img {
      height: 12px;
      margin-right: 0.5rem;
    }
  }
  .cover-photo {
    height: 7rem;
    width: 7rem;
    margin-left: 1rem;
    margin-top: 1rem;
    object-fit: cover;
    border-radius: 8px;
    cursor: pointer;
  }
  .highlights-summary-container {
    border-bottom: 1px solid $soft-gray;
    height: 65vh;
    overflow-y: auto;
  }
  .summary-buttons-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 1rem;
  }
  .summary-button {
    @include gray-text-button();
    margin: 0 0.5rem;
    padding: 8px 16px;
    img {
      height: 12px;
      margin-right: 0.5rem;
    }
  }
  .dark-button {
    @include dark-blue-button();
    padding: 8px 16px;
    img {
      filter: invert(99%);
    }
  }
  .wide {
    width: 90%
  }
  .article-title {
    color: $dark-green;
    cursor: pointer;
    font-size: 16px;
  }
  .article-preview {
    color: $base-gray;
    font-size: 14px;
  }
  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid $soft-gray;
    padding-top: 0.5rem;
    span {
      font-size: 12px;
      margin-right: 0.5rem;
    }
  }
  .footer-icon-container {
    display: flex;
    align-items: center;
  }
  .right-arrow-footer {
    height: 16px;
    margin-left: 1rem;
    cursor: pointer;
  }
  .footer-icon {
    height: 14px;
    margin-left: 1rem;
    cursor: pointer;
  }
  .author-time {
    color: $light-gray-blue;
  }
  .divier-dot {
    position: relative;
    bottom: 0.2rem;
  }
  .large-dot {
    font-size: 40px;
    bottom: 1.7rem;
    margin-right: 0.75rem;
  }
  .gray-background {
    display: flex;
    align-items: center;
    background-color: $soft-gray;
    height: 4vh;
    width: 11vw;
    border-radius: 8px;
  }
  .toggle-container {
    border: 1px solid $soft-gray;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    width: 5vw;
    height: 3vh;
    border-radius: 8px;
    margin: 0 0.25rem;
    color: $light-gray-blue;
    p {
      margin: 0;
      font-size: 12px;
      // text-align: center;
    }
  }
  .active {
    background-color: $white;
    border-radius: 8px;
    color: $dark-black-blue;
  }
  .updated-time {
    font-size: 12px;
    color: $light-gray-blue;
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.5rem;
    margin-top: 0.5rem;
    margin-right: 1rem;
  }
  .search {
    height: 12px;
    margin-right: 0.5rem;
    filter: invert(20%);
  }
  .search-bar {
    // background-color: white;
    border: 1px solid $very-light-gray;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3px 6px;
    border-radius: 8px;
    // margin-top: 16px;
    height: 4vh;
  }
  [type='search']::-webkit-search-cancel-button {
    -webkit-appearance: none;
    appearance: none;
  }
  input[type='search'] {
    width: 6.5vw;
    letter-spacing: 0.75px;
    border: none;
    padding: 4px 0;
    margin: 0;
    background: none;
    font-size: 12px;
  }
  input[type='search']:focus {
    outline: none;
  }
  ::placeholder {
    color: $very-light-gray;
    font-size: 12px;
  }
  .highlights {
    margin-top: 0;
  }
  .small-title-text {
    font-size: 14px;
    color: $light-gray-blue;
    img {
      height: 12px;
      margin-right: 0.5rem;
      filter: invert(63%) sepia(9%) saturate(735%) hue-rotate(200deg) brightness(95%) contrast(92%);
    }
  }
</style>