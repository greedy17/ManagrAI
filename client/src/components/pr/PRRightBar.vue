<template>
  <div class="right-bar">
    <div v-if="selectedArticle" class="right-content">
      <div>
        <h3 class="right-bar-title">{{truncateTitle(selectedArticle.title)}}</h3>
      </div>
      <div class="gray-background">
        <div class="toggle-container" :class="selectedResource === 'Source' ? 'active' : ''" @click="changeResource('Source')">
          <p>Source</p>
        </div>
        <div class="toggle-container" :class="selectedResource === 'Data' ? 'active' : ''" @click="changeResource('Data')">
          <p>Data</p>
        </div>
        <div class="toggle-container" :class="selectedResource === 'Chat' ? 'active' : ''" @click="changeResource('Chat')">
          <p>Chat</p>
        </div>
      </div>
      <div v-if="selectedResource === 'Data'" class="data-container">
        <div v-if="loading">
          Loading...
        </div>
        <div v-else-if="!Object.keys(selectedArticle.data).length" @click="setData" class="add-edit-button">
          <img src="@/assets/images/sparkles-round.svg" class="button-img margin-right" /><span>Auto-populate fields</span>
        </div>
        <div v-else class="right-side">
          <img src="@/assets/images/sparkles-round.svg" class="button-img" />
        </div>
        <div class="data-content">
          <div>
            <p class="data-title">Impact Score</p>
            <p class="data-detail">{{ selectedArticle.data.impactScore }}</p>
          </div>
          <div>
            <p class="data-title">Impact Score Details</p>
            <p class="data-detail">{{ selectedArticle.data.impactScoreDetails }}</p>
          </div>
          <div>
            <p class="data-title">Key Messages</p>
            <p class="data-detail">{{ selectedArticle.data.keyMessages }}</p>
          </div>
          <div>
            <p class="data-title">Summary / Notes</p>
            <p class="data-detail">{{ selectedArticle.data.summary }}</p>
          </div>
          <div>
            <p class="data-title">Topics</p>
            <p class="data-detail">{{ selectedArticle.data.topics }}</p>
          </div>
          <div>
            <p class="data-title">Competitors</p>
            <p class="data-detail">{{ selectedArticle.data.competitors }}</p>
          </div>
          <div>
            <p class="data-title">Products</p>
            <p class="data-detail">{{ selectedArticle.data.products }}</p>
          </div>
          <div>
            <p class="data-title">Follow up</p>
            <p class="data-detail">{{ selectedArticle.data.followUp }}</p>
          </div>
        </div>
        <div class="add-edit-button">
          <img src="@/assets/images/edit-round.svg" class="button-img margin-right" /> <span>Add / Edit</span>
        </div>
      </div>
      <div v-else>
        {{ selectedResource }}
      </div>
    </div>
    <div v-else class="right-content">
      <h3>Please select an article</h3>
    </div>
  </div>
</template>
<script>
export default {
  name: 'PRRightBar',
  components: {

  },
  props: {
    
  },
  data() {
    return {
      selectedResource: 'Data',
      loading: false,
    }
  },
  watch: {

  },
  created() {

  },
  methods: {
    changeResource(resource) {
      this.selectedResource = resource
    },
    truncateTitle(title) {
      if (title.length <= 33) {
        return title
      }
      const titleSplit = title.split(' ')
      let newTitle = ''
      for (let i = 0; i < titleSplit.length; i++) {
        const word = titleSplit[i]
        newTitle += `${word} `
        if (newTitle.length >= 30) {
          const lastChar = newTitle[newTitle.length-2]
          if (lastChar === ',' || lastChar === '.') {
            newTitle = newTitle.slice(0, newTitle.length-2)
          } else {
            newTitle = newTitle.slice(0, newTitle.length-1)
          }
          newTitle += '...'
          break;
        }
      }
      return newTitle
      // return title.slice(0, 34) + '...'
    },
    setData() {
      this.loading = true
      setTimeout(() => {
        let articleCopy = {...this.selectedArticle}
        articleCopy.data = {
          impactScore: 8,
          impactScoreDetails: 'Talked positively about Tesla',
          keyMessages: `Tesla revolutionizes the automotive industry with sustainable innovation.`,
          summary: `The article discusses projections for U.S. new-vehicle sales in 2023 and lists the best-selling...`,
          topics: `Auto, Ford, Truck, Electric cars`,
          competitors: `Ford`,
          products: `Tesla Model X`,
          followUp: `No follow up is required`,
        }
        this.$store.dispatch('updateSelectedArticle', articleCopy)
        this.loading = false
        // this.selectedArticle.data = {}
      }, 1500)
    },
  },
  computed: {
    selectedArticle() {
      return this.$store.state.selectedArticle
    },
  }
}
</script>
<style lang="scss" scoped>
  @import '@/styles/variables';
  @import '@/styles/buttons';
  .right-bar {
    margin: 1rem 0.5rem 0.5rem 0.5rem;
    background-color: $white;
    // width: 23vw;
    position: sticky;
    width: 100%;
    // height: 100%;
    border-radius: 8px;
  }
  .display-flex {
    display: flex;
  }
  .right-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0.5rem;
  }
  .right-bar-title {
    // text-align: center;
  }
  .gray-background {
    display: flex;
    align-items: center;
    background-color: $soft-gray;
    height: 5vh;
    // width: 16vw;
    width: 90%;
    border-radius: 8px;
  }
  .toggle-container {
    border: 1px solid $soft-gray;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    // width: 5vw;
    width: 30%;
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
  .button-img {
    height: 14px;
  }
  .margin-right {
    margin-right: 0.5rem;
  }
  .right-side {
    display: flex;
    justify-content: flex-end;
    width: 100%;
  }
  .data-title {
    font-size: 14px;
    color: $light-gray-blue;
    margin-bottom: 0.25rem;
  }
  .data-detail {
    font-size: 13px;
    // color: $light-gray-blue;
    margin-top: 0.25rem;
    margin-left: 0.25rem;
    min-height: 1.5rem;
  }
  .data-container {
    width: 90%;
    margin-top: 1rem;
  }
  .data-content {
    height: 65vh;
    // border: 1px solid red;
    overflow-y: auto;
  }
  .add-edit-button {
    @include gray-text-button();
    padding-bottom: 0.5rem;
    padding-top: 0.5rem;
    position: relative;
    bottom: 0rem;
  }
</style>