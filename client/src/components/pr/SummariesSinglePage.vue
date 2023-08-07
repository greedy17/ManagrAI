<template>
  <div class="main-content">
    <Modal
      v-if="regenModal"
      @close-modal="
        () => {
          $emit('cancel'), closeRegenModal()
        }
      "
      class="regen-modal"
    >
      <div class="regen-container">
        <div class="regen-header">
          <div>
            <h4 class="regen-header-title">New Search</h4>
            <p class="regen-header-subtitle">Create a new search using conversational AI</p>
          </div>
          <div class="pointer" @click="closeRegenModal">X</div>
        </div>
        <div class="regen-body">
          <div>
            <div>
              <h5 class="regen-body-title">Search</h5>
              <span class="regen-header-subtitle">Use conversation text. AI will convert it to a boolean.</span>
            </div>
            <textarea 
              v-model="newSearch" 
              class="regen-body-text"
            />
          </div>
          <div>
            <div>
              <h5 class="regen-body-title">Summary Instructions <span class="regen-header-subtitle">(optional)</span></h5>
            </div>
            <textarea 
              v-model="newTemplate" 
              class="regen-body-text"
            />
          </div>
          <div class="blue-border-button">Use a Template</div>
        </div>
        <div class="regen-footer">
          <div class="cancel-button" @click="closeRegenModal">Cancel</div>
          <div class="save-button" @click="generateNewSearch">Save</div>
        </div>
      </div>
    </Modal>
    <div v-if="page === 'SUMMARIES'">
      <div v-if="!selectedSearch">
        <div>
          <img src="@/assets/images/logo.png" class="logo" />
          <p>Generate a news summary from over 1 million sources.</p>
        </div>
        <div>
          <div class="new-summary-bow">
            <div>
              <img />
              <span>Searches</span>
            </div>
            <div>
              <input 
                placeholder="Start a new search"
                v-model="newSearch"
              />
            </div>
          </div>
          <div class="new-summary-bow">
            <div>
              <img />
              <span>Templates</span>
            </div>
            <div>
              <textarea 
                placeholder="Provide additional instructions. This step is optional."
                v-model="newTemplate"
              />
            </div>
          </div>
          <div class="new-summary-bow">
            <div>
              <span>Additional sources</span>
            </div>
            <div>
              <input 
                placeholder="Separate with commas"
                v-model="additionalSources"
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
      <div v-else class="loaded-content">
        <div v-if="summaryLoading" class="summaries-container">Generating news summary...</div>
        <div v-else class="summaries-container">
          <div class="label-width">
            <img class="logo" src="@/assets/images/sparkles-nofill-round.svg" />
            <span>Summary</span>
          </div>
          <div class="content-width">
            <div>
              Summary for {{ selectedSearch.search }}
            </div>
            <div>
              {{summary}}
            </div>
            <div>
              <div @click="openRegenModal">Regenerate</div>
              <div>Save Search</div>
            </div>
          </div>
        </div>
        <div v-if="loading" class="clips-container">Gathering news articles...</div>
        <div v-else class="clips-container">
          <div class="label-width">
            <img class="logo" src="@/assets/images/list.svg" />
            <span>Articles</span>
          </div>
          <div class="content-width">
            <div v-for="article in filteredArticles" :key="article.url" class="">
              <div class="card">
                <div class="display-flex">
                  <div class="">
                    <div class="card-top-left">
                      <img :src="article.icon" />
                      <span>{{ article.source.name }}</span>
                    </div>
                    <h3 class="article-title" @click="goToArticle(article.url)">
                      {{ article.title }}
                    </h3>
                    <pre v-html="article.description" class="article-preview" />
                  </div>
                  <div @click="goToArticle(article.link)">
                    <img :src="article.urlToImage" class="cover-photo" />
                  </div>
                </div>
                <div class="card-footer">
                  <div class="author-time">
                    <span>{{ article.publishedAt.split('T')[0] }}</span>
                    <span class="divier-dot">.</span>
                    <span>{{ article.author }}</span>
                  </div>
                  <div class="footer-icon-container">
                    <div>
                      <img src="@/assets/images/sparkles-nofill-round.svg" class="logo" />
                      <span>Summarize Article</span>
                    </div>
                    <div>
                      <img src="@/assets/images/tags.svg" class="logo" />
                      <span>Tag</span>
                    </div>
                    <!-- <div v-if="newSummary" class="">
                      <input type="checkbox" />
                    </div> -->
                    <!-- <img src="@/assets/images/sparkles-nofill-round.svg" class="footer-icon" /> -->
                    <!-- <img src="@/assets/images/tags.svg" class="footer-icon" /> -->
                    <!-- <img src="@/assets/images/search-round.svg" class="footer-icon" /> -->
                    <!-- <img src="@/assets/images/arrow-small-right.svg" class="right-arrow-footer" /> -->
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
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  props: {
    selectedSearch: {
      type: Object,
    },
    page: {
      type: String
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
      regenModal: false,
      filteredArticles: [],
      summary: '',
      newSummary: false,
    }
  },
  watch: {},
  created() {},
  methods: {
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
      } catch(e){
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
    openRegenModal() {
      this.regenModal = true
    },
    closeRegenModal() {
      this.regenModal = false
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
            this.filteredArticles = JSON.parse(response.articles)
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
    },
    getArticleURLs(articles) {
      return articles.map(a => a.url)
    },
    async getSummary(clips, search = '', instructions = '') {
      const urls = this.getArticleURLs(clips)
      const data = {
        clips: urls,
        search,
        instructions,
      }
      try {
        this.summaryLoading = true
        const res = await Comms.api.getSummary(data)
        this.summary = res.summary
      } catch(e) {
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
.main-content {
  display: flex;
  background-color: $white;
  border-radius: 8px;
  margin: 1rem 0.5rem 0.5rem 0;
  padding: 1rem;
  min-height: 86vh;
  width: 92vw;
  color: $dark-black-blue;
}
.loaded-content {
  // display: flex;
  // justify-content: space-between;
  // width: 92vw;
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
.article-title {
  color: $dark-green;
  cursor: pointer;
  font-size: 16px;
}
.article-preview {
  color: $base-gray;
  font-family: $base-font-family;
  font-size: 14px;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0;
  margin: 0 0 0.5rem 0;
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
.author-time {
  color: $light-gray-blue;
}
.divier-dot {
  position: relative;
  bottom: 0.2rem;
}
.footer-icon {
  height: 14px;
  margin-left: 1rem;
  cursor: pointer;
}
.right-arrow-footer {
  height: 16px;
  margin-left: 1rem;
  cursor: pointer;
}
.summaries-container {
  display: flex;
  justify-content: space-between;
  height: 40vh;
  width: 90vw;
}
.clips-container {
  display: flex;
  justify-content: space-between;
  height: 40vh;
  width: 90vw;
}
.label-width {
  display: flex;
  // width: 50vw;
}
.content-width {
  width: 70vw;
  overflow-y: auto;
}
.regen-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid $soft-gray;
  margin-bottom: 1rem;
}
.regen-header-title {
  margin: 0.25rem 0;
}
.regen-header-subtitle {
  font-size: 12px;
  color: $light-gray-blue;
  margin: 0.5rem 0;
}
.regen-body {
  margin: 0.5rem 0;
  border-bottom: 1px solid $soft-gray;
}
.regen-body-title {
  margin: 0 0 0 0;
}
.regen-body-text {
  resize: none;
  outline: none;
  border: 1px solid $soft-gray;
  border-radius: 8px;
  height: 4rem;
  width: 25rem;
  overflow-y: auto;
  margin: 1rem 0;
  padding: 0.75rem;
  font-family: $base-font-family;
}
.regen-footer {
  display: flex;
  justify-content: flex-end;
}
.blue-border-button {
  @include dark-blue-border-button();
  width: 8rem;
  margin-bottom: 1rem;
}
.cancel-button {
  @include gray-text-button();
}
.save-button {
  @include dark-blue-button();
  margin-left: 0.5rem;
}
.pointer {
  cursor: pointer;
}
.regen-modal {
  margin-top: 10rem;
}
</style>