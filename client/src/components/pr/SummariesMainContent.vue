<template>
  <div class="main-content">
    <div class="left-content">
      <div>
        <div class="display-flex">
          <p>Summary</p>
          <p>Chat</p>
        </div>
        <div>
          <p>Summary</p>
        </div>
      </div>
      <div>
        <div v-if="!summary">
          <button @click="generateSummary">Generate Summary</button>
        </div>
        <div v-else>
          <div>
            <div>
              <h3>Highlights:</h3>
              <div v-for="(highlight, i) in summary.highlights" :key="i">
                <div>{{ highlight }}</div>
              </div>
            </div>
            <div>
              <h3>Overall Summary:</h3>
              <div>{{ summary.overview }}</div>
            </div>
          </div>
          <div>
            <button>Regenerate</button>
            <button>New Summary</button>
          </div>
        </div>
      </div>
    </div>
    <div class="right-content">
      <div class="space-between">
        <div>
          <p>Results: {{ articles.length }}</p>
        </div>
        <div>
          <img src="" />
          <input placeholder="Search" />
        </div>
      </div>
      <div v-for="article in articles" :key="article.id" class="card">
        <div class="display-flex">
          <div class="">
            <div class="display-flex">
              <img :src="article.icon" />
              <span>{{ article.source }}</span>
            </div>
            <h3>{{ article.title }}</h3>
            <h4>{{ article.preview }}</h4>
          </div>
          <div>
            <img :src="article.coverPhoto" class="cover-photo" />
          </div>
        </div>
        <div class="display-flex">
          <div class="display-flex">
            <span>{{ article.time }}</span>
            <span>.</span>
            <span>{{ article.author }}</span>
          </div>
          <div class="display-flex">
            <span>Icon 1</span>
            <span>Icon 2</span>
            <span>Icon 3</span>
            <span>Icon 4</span>
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
    }
  },
  watch: {

  },
  created() {
    this.getArticles()
  },
  methods: {
    async generateSummary() {
      const res = {
        overview: 'Tesla is cool and all but have you tried robbing an ice cream store at 4am while your pregnant wife screams at you from the car?',
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
          icon: '',
          source: 'MarketWatch',
          title: 'EV stocks see green after Tesla, Rivian, Nio report upbeat deliveries data',
          preview: `Electric-vehicle maker stocks got a broad boost Monday, after upbeat delivery and production data from a host of companies in the U.S. and...`,
          coverPhoto: `https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/New_York_City_%28New_York%2C_USA%29%2C_Empire_State_Building_--_2012_--_6448.jpg/1200px-New_York_City_%28New_York%2C_USA%29%2C_Empire_State_Building_--_2012_--_6448.jpg`,
          time: '5 mins ago',
          author: 'Eric Peters',
        },
      ]
      this.articles = res
    },
  },
  computed: {
    
  }
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
  .main-content {
    display: flex;
  }
  .display-flex {
    display: flex;
  }
  .space-between {
    display: flex;
    justify-content: space-between;
  }
  .left-content {
    width: 30vw;
  }
  .right-content {
    width: 30vw;
  }
  .card {
    border: 1px solid $soft-gray;
  }
  .cover-photo {
    height: 8rem;
    width: 8rem;
    object-fit: cover;
  }
</style>