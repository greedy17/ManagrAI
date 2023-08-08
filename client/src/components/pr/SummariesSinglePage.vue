<template>
  <div class="main-content">
    <div class="center" v-if="page === 'SUMMARIES'">
      <div class="no-content" v-if="!selectedSearch">
        <div class="title-row">
          <!-- <img src="@/assets/images/logo.png" class="logo" /> -->
          <p class="typed" v-if="!newSearch">
            Generate a news summary from over 1 million sources.
          </p>
          <p v-else>
            Hey Managr, summarize <span class="search-text">"{{ newSearch }}"</span>
          </p>
        </div>
        <div>
          <div class="input-container">
            <div class="input-row">
              <div class="main-text">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
              </div>

              <input
                autofocus
                class="area-input"
                placeholder="Start a new search"
                v-model="newSearch"
                @keydown.enter.exact.prevent="generateNewSearch"
              />
              <img
                :class="{ invert: !message }"
                src="@/assets/images/paper-plane.svg"
                height="14px"
                alt=""
              />
            </div>
          </div>

          <!-- <div class="input-container">
            <div class="input-row">
              <div class="main-text">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
              </div>

              <input
                autofocus
                class="area-input"
                placeholder="Provide additional instructions. This step is optional."
                v-model="newTemplate"
              />
            </div>
          </div>

          <div class="input-container">
            <div class="input-row">
              <div class="main-text">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
              </div>

              <input
                autofocus
                class="area-input"
                placeholder="Separate with commas"
                v-model="additionalSources"
              />
            </div>
          </div> -->

          <div class="center">
            <button class="secondary-button">Add Instructions</button>
            <button class="secondary-button">Add Sources</button>
          </div>
        </div>
      </div>
      <div v-else class="loaded-content">
        <div v-if="summaryLoading" class="summaries-container">
          Summarizing coverage for {{ newSearch }}
        </div>
        <div v-else class="summaries-container">
          <div class="content-width">
            <div class="news-container">
              <div>Summary for {{ selectedSearch.search }}</div>
              <pre class="pre-text" v-html="summary"></pre>
              <div>
                <div>Regenerate</div>
                <div>Save Search</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="!loading" class="clips-container">
          <div class="content-width">
            <div v-for="article in filteredArticles" :key="article.id" class="news-container">
              <div class="news-card" @click="selectArticle(article)">
                <header>
                  <div class="card-col">
                    <div class="card-top-left">
                      <!-- <img :src="article.icon" /> -->
                      <span>{{ article.source.name }}</span>
                    </div>
                    <h1 class="article-title" @click="goToArticle(article.url)">
                      {{ article.title }}
                    </h1>
                    <p @click="getArticleSummary(article.url)" class="article-preview">
                      {{ article.description }}
                    </p>
                  </div>

                  <div @click="goToArticle(article.link)">
                    <img :src="article.urlToImage" class="cover-photo" />
                  </div>
                </header>

                <div class="card-footer">
                  <div class="author-time">
                    <span class="author">{{ article.author }}</span>
                    <span class="divier-dot">.</span>
                    <span class="off-gray">{{
                      getTimeDifferenceInMinutes(article.publishedAt)
                    }}</span>
                  </div>
                  <div class="footer-icon-container">
                    <!-- <div v-if="newSummary" class="">
                      <input type="checkbox" @click="addRemoveSelectedArticles(article)" />
                    </div> -->

                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" class="left-mar">
                      <path
                        d="M17.5 1.25a.5.5 0 0 1 1 0v2.5H21a.5.5 0 0 1 0 1h-2.5v2.5a.5.5 0 0 1-1 0v-2.5H15a.5.5 0 0 1 0-1h2.5v-2.5zm-11 4.5a1 1 0 0 1 1-1H11a.5.5 0 0 0 0-1H7.5a2 2 0 0 0-2 2v14a.5.5 0 0 0 .8.4l5.7-4.4 5.7 4.4a.5.5 0 0 0 .8-.4v-8.5a.5.5 0 0 0-1 0v7.48l-5.2-4a.5.5 0 0 0-.6 0l-5.2 4V5.75z"
                        fill="#000"
                      ></path>
                    </svg>
                    <img src="@/assets/images/sparkles-thin.svg" class="right-arrow-footer" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="page === 'PITCHES'">
      <div>
        <div>
          <img src="@/assets/images/logo.png" class="logo" />
          <p>Generate a pitch or blog post based on any persona.</p>
        </div>
        <div>
          <div class="new-summary-bow">
            <div>
              <img />
              <span>Your Brand</span>
            </div>
            <div>
              <input
                placeholder="Lululemon, a global leader in athletic apparel"
                v-model="brandName"
              />
            </div>
          </div>
          <div class="new-summary-bow">
            <div>
              <img />
              <span>Target Persona</span>
            </div>
            <div>
              <textarea
                placeholder="A lifestyle and fitness reporter at 'The Wall Street Journal' who focuses on retail trends and consumer goods."
                v-model="targetPersona"
              />
            </div>
          </div>
          <div class="new-summary-bow">
            <div>
              <span>Output Instructions</span>
            </div>
            <div>
              <textarea
                placeholder="Create a pitch for our new line of sustainably producted yoga wear, designed to appeal to eco-conscious consumers. A compelling pitch document that underscores the sustainable features..."
                v-model="outputInstructions"
              />
            </div>
          </div>
          <div>
            <div @click="clearNewSearch">
              <div>Clear</div>
            </div>
            <div @click="generateNewSearch">
              <div>Submit</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import ChatTextBox from '../Chat/ChatTextBox.vue'
import Comms from '@/services/comms'

export default {
  name: 'SummariesSinglePage',
  components: {
    ChatTextBox,
  },
  props: {
    selectedSearch: {
      type: Object,
    },
    page: {
      type: String,
    },
  },
  data() {
    return {
      newSearch: '',
      newTemplate: '',
      additionalSources: '',
      brandName: '',
      targetPersona: '',
      additionalSources: '',
      outputInstructions: '',
      loading: false,
      summaryLoading: false,
      filteredArticles: [],
      summary: '',
      newSummary: false,
    }
  },
  watch: {},
  created() {},
  methods: {
    getTimeDifferenceInMinutes(dateString) {
      const currentDate = new Date()
      const givenDate = new Date(dateString)

      if (
        givenDate.getDate() === currentDate.getDate() &&
        givenDate.getMonth() === currentDate.getMonth() &&
        givenDate.getFullYear() === currentDate.getFullYear()
      ) {
        const timeDifferenceInMilliseconds = currentDate - givenDate
        const timeDifferenceInMinutes = Math.floor(timeDifferenceInMilliseconds / (1000 * 60))
        if (timeDifferenceInMinutes >= 60) {
          const timeDifferenceInHours = Math.floor(timeDifferenceInMinutes / 60)
          const remainingMinutes = timeDifferenceInMinutes % 60
          return `${timeDifferenceInHours}h`
        } else {
          return `${timeDifferenceInMinutes}m`
        }
      } else {
        return `${givenDate.getMonth() + 1}/${givenDate.getDate()}/${givenDate.getFullYear()}`
      }
    },
    async generateNewSearch() {
      if (!this.newSearch) {
        return
      }
      this.loading = true
      this.summaryLoading = true
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      try {
        this.getClips().then((response) => {
          this.getSummary(this.filteredArticles, '', this.newTemplate)
        })
      } catch (e) {
        console.log(e)
      }

      this.newSearch = ''
      this.newTemplate = ''
    },
    clearNewSearch() {
      this.newSearch = ''
      this.newTemplate = ''
      this.additionalSources = ''
      this.brandName = ''
      this.targetPersona = ''
      this.outputInstructions = ''
    },
    changeSearch(search) {
      this.$emit('change-search', search)
    },
    async getClips() {
      try {
        await Comms.api
          .getClips({
            search: this.newSearch,
          })
          .then((response) => {
            this.filteredArticles = response.articles
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
    },
    getArticleDescriptions(articles) {
      return articles.map((a) => a.description)
    },
    async getSummary(clips, search = '', instructions = '') {
      const urls = this.getArticleDescriptions(clips)
      const data = {
        clips: urls,
        search,
        instructions,
      }
      try {
        this.summaryLoading = true
        const res = await Comms.api.getSummary(data)
        this.summary = res.summary
      } catch (e) {
        console.log('Error in getSummary', e)
        this.$toast('Something went wrong, please try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.summaryLoading = false
      }
    },
    async getArticleSummary(url, instructions = null) {
      console.log(url)
      try {
        await Comms.api
          .getArticleSummary({
            url: url,
            search: this.newSearch,
            instructions: instructions,
          })
          .then((response) => {
            console.log(response)
          })
      } catch (e) {
        console.log(e)
      }
    },
    regenNewSummary() {
      this.getSummary(this.filteredArticles, '', this.message)
      this.changeRegen()
      this.message = ''
    },
    changeSummaryChat(type) {
      this.summaryChat = type
      this.scrollToBottom()
    },
    selectArticle(article) {
      this.$store.dispatch('updateSelectedArticle', article)
    },
    saveSelectedArticles() {
      this.getSummary(this.selectedArticles)
      this.selectedArticles = []
      this.changeNew()
    },
    addRemoveSelectedArticles(article) {
      const existingArticle = this.selectedArticles.filter((ar) => ar.url === article.url)[0]
      if (existingArticle) {
        this.selectedArticles = this.selectedArticles.filter((ar) => ar.url !== article.url)
      } else {
        this.selectedArticles.push(article)
      }
    },
    goToArticle(link) {
      window.location.href = link
    },
    changeRegen() {
      this.regenSummary = !this.regenSummary
    },
    changeNew() {
      this.newSummary = !this.newSummary
    },
    searchTitles() {
      this.filteredArticles = this.articles.filter((article) =>
        article.title.includes(this.filterText),
      )
    },
    scrollToBottom() {
      setTimeout(() => {
        const chatWindow = this.$refs.chatWindow
        setTimeout(() => {
          chatWindow.scrollTop = chatWindow.scrollHeight
        }, 200)
      }, 0)
    },
  },
  computed: {
    messages() {
      return this.$store.state.messages
    },
    userName() {
      return this.$store.state.user.firstName
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

@keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

@keyframes blinking {
  0% {
    border-right-color: transparent;
  }
  50% {
    border-right-color: rgb(66, 65, 65);
  }
  100% {
    border-right-color: transparent;
  }
}

.typed {
  overflow: hidden;
  white-space: nowrap;
  width: 0;
  animation: typing 1.5s steps(30, end) forwards, blinking 1s infinite;
  border-right: 1px solid;
}

.search-text {
  color: $dark-black-blue;
  font-weight: 900;
  color: #6b6b6b;
}

.primary-button {
  @include dark-blue-button();
  padding: 10px 12px;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.secondary-button {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  background-color: white;
  padding: 10px 12px;
  img {
    filter: invert(25%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}
.center {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 24px;
  button:first-of-type {
    margin-right: 1rem;
  }
}
.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.2rem 0.75rem 1.2rem;
  border-radius: 6px;
  width: 500px;
  background-color: $offer-white;
  color: $base-gray;
}
.area-input {
  width: 100%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $base-font-family !important;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
}

.area-input:disabled {
  cursor: not-allowed;
}

.area-input::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $base-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}
.input-row {
  display: flex;
  align-items: center;
  flex-direction: row;
  align-items: center;
}

.main-text {
  display: flex;
  flex-direction: row;
  align-items: center;
  white-space: nowrap;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  padding-right: 1rem;
  margin: 0;
  svg {
    margin-right: 8px;
  }
}

.main-content {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  border-radius: 8px;
  padding: 58px 36px 0 36px;
  height: fit-content;
  width: 100vw;
  color: $dark-black-blue;
  overflow-y: scroll;
}
.pre-text {
  color: $dark-black-blue;
  font-family: $base-font-family;
  font-size: 14px;
  font-weight: 400;
  line-height: 24px;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0;
  margin: 0;
}
.loaded-content {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
}
.no-content {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  height: 60vh;
  width: 700px;
}

.title-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 14px;
  margin-bottom: 1rem;
  img {
    margin-right: 1rem;
  }
}
.display-flex {
  display: flex;
}
.space-between {
  display: flex;
  justify-content: space-between;
}
.logo {
  height: 20px;
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
.highlights-summary-container {
  border-bottom: 1px solid $soft-gray;
  height: 65vh;
  overflow-y: auto;
  padding: 0 1rem;
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
.summaries-container {
  display: flex;
  justify-content: flex-start;
  width: 100%;
}
// .clips-container {
//   display: flex;
//   justify-content: flex-start;
//   width: 100%;
// }
.label-width {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  height: fit-content;
  img {
    margin: 0;
    padding: 0;
    margin-right: 8px;
  }
}
.content-width {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  overflow-y: auto;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  height: 120px;
  overflow: none;
  text-overflow: ellipsis;
  margin-bottom: 2rem;
}

.news-container {
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.author {
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
  max-width: 200px;
  min-height: 22px;
  text-overflow: ellipsis;
  background-color: $soft-gray;
  padding: 4px 12px;
  color: $base-gray;
  border-radius: 12px;
}

.off-gray {
  color: #6b6b6b;
}

.news-card {
  position: relative;
  min-height: 220px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 1rem 0;
  margin-bottom: 1rem;
}

.card-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.card:hover {
  transform: scale(1.025);
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
  height: 112px;
  width: 116px;
  margin-left: 1rem;
  margin-top: 1.25rem;
  object-fit: cover;

  cursor: pointer;
}

.article-title {
  font-size: 16px;
  font-weight: 900;
  line-height: 24px;
  letter-spacing: 0;
  color: $base-gray;
  margin: 12px 0;
  max-width: 500px;
  white-space: nowrap;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
}

.article-preview {
  color: $base-gray;
  font-size: 14px;
  height: 68px;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  font-weight: 400;
  margin: 0;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-top: 1rem;
  span {
    font-size: 12px;
    margin-right: 0.5rem;
  }
}
.footer-icon-container {
  display: flex;
  align-items: center;
  margin-right: 8px;
}
.right-arrow-footer {
  height: 16px;
  margin-left: 1rem;
  cursor: pointer;
}
.left-mar {
  margin-left: 1rem;
}
.footer-icon {
  height: 24px;
  margin-left: 1rem;
  cursor: pointer;
}
.author-time {
  display: flex;
  align-items: center;
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
</style>