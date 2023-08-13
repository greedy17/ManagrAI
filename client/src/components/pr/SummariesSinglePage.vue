<template>
  <div class="main-content">
    <Modal v-if="regenModal" class="regen-modal">
      <div class="regen-container">
        <div class="regen-header">
          <div>
            <h4 class="regen-header-title">New Search</h4>
            <p class="regen-header-subtitle">Create a new search using conversational AI</p>
          </div>
          <div class="pointer" @click="closeRegenModal"><small>X</small></div>
        </div>
        <div class="regen-body">
          <div>
            <div>
              <h5 class="regen-body-title">Search</h5>
              <span class="regen-header-subtitle"
                >Use conversation text. AI will convert it to a boolean.</span
              >
            </div>
            <textarea v-autoresize v-model="newSearch" class="regen-body-text" />
          </div>
          <div>
            <div>
              <h5 class="regen-body-title">
                Summary Instructions <span class="regen-header-subtitle">(optional)</span>
              </h5>
            </div>
            <textarea v-autoresize v-model="newTemplate" class="regen-body-text" />
          </div>
          <div class="blue-border-button">Use a Template</div>
        </div>
        <div class="regen-footer">
          <div class="cancel-button" @click="closeRegenModal">Cancel</div>
          <div class="save-button" @click="generateNewSearch">Save</div>
        </div>
      </div>
    </Modal>
    <div ref="loadedContent" class="center" v-if="page === 'SUMMARIES'">
      <div class="no-content" v-if="!selectedSearch">
        <div class="title-row">
          <!-- <p v-if="typedMessage" :class="{ typed: isTyping }">{{ typedMessage }}</p>
            <p style="opacity: 0" v-else>...</p> -->
          <p v-if="!newSearch" class="typed">Generate a summary from over 1 million sites</p>

          <p v-else>
            Summarize coverage for <span class="search-text">"{{ newSearch }}"</span>
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
                :class="{ invert: !newSearch }"
                src="@/assets/images/paper-plane.svg"
                height="14px"
                alt=""
                @click="generateNewSearch"
                class="pointer"
              />
            </div>
          </div>

          <div v-if="addingPrompt" style="margin-top: 1rem" class="input-container">
            <div class="input-row">
              <div class="main-text">
                <img
                  style="margin-right: 8px"
                  src="@/assets/images/sparkles-thin.svg"
                  height="18px"
                />
              </div>
              <textarea
                rows="1"
                class="area-input"
                placeholder="What would you like included in the summary?"
                v-model="newTemplate"
                v-autoresize
              />
              <small @click="removePrompt" class="remove">X</small>
            </div>
          </div>

          <div v-if="addingSources" style="margin-top: 1rem" class="input-container">
            <div class="input-row">
              <div class="main-text">
                <img style="margin-right: 8px" src="@/assets/images/globe.svg" height="20px" />
              </div>
              <input
                autofocus
                class="area-input"
                placeholder="Paste additional news sites, separate using commas"
                v-model="additionalSources"
              />
              <small @click="removeSource" class="remove">X</small>
            </div>
          </div>

          <div class="center mar-top">
            <button @click="toggleAddPrompt" v-if="!addingPrompt" class="secondary-button">
              Custom Prompt
            </button>
            <button @click="toggleAddSource" v-if="!addingSources" class="secondary-button">
              Add Sources
            </button>

            <button
              @click="generateNewSearch"
              v-if="addingSources || addingPrompt"
              class="primary-button"
            >
              Submit
            </button>
          </div>
        </div>
      </div>
      <div v-else class="loaded-content">
        <div style="width: 50%" :class="{ 'neg-lmar': !loading }" v-if="summaryLoading">
          <div :class="{ 'left-mar': loading }" class="row">
            <img src="@/assets/images/logo.png" class="blue-logo" height="16px" alt="" />
            <p class="summary-load-text">Generating Summary...</p>
          </div>

          <div :class="{ 'neg-l-mar': !loading }" class="summary-preview-skeleton shimmer">
            <div class="content">
              <!-- <div class="title-wide"></div> -->
              <div class="meta-wide"></div>
              <div class="meta-shorter"></div>
            </div>

            <!-- <div class="skeleton-bar">
              <div class="row">
                <div class="skeleton-button"></div>
                <div class="skeleton-button"></div>
              </div>
              <div class="skeleton-icon"></div>
            </div>
            <div class="excerpt-wide"></div>
            <div class="excerpt-wide"></div>
            <div class="excerpt-wide"></div> -->
          </div>
        </div>
        <div v-else class="summaries-container">
          <div class="content-width">
            <div class="news-container">
              <div class="title-container">
                <h1 class="no-text-margin">{{ selectedSearch.search }}</h1>
                <p class="sub-text">
                  AI generated search: <span>{{ booleanString }}</span>
                </p>
              </div>
              <div class="title-bar">
                <div class="row">
                  <button
                    :disabled="articleSummaryLoading || loading || summaryLoading || savingSearch"
                    @click="openRegenModal"
                    class="secondary-button"
                  >
                    {{ filteredArticles.length ? 'Regenerate' : 'New Search' }}
                  </button>
                  <button
                    @click="createSearch"
                    v-if="filteredArticles.length"
                    :disabled="articleSummaryLoading || loading || summaryLoading || savingSearch"
                    class="primary-button"
                  >
                    <img
                      v-if="savingSearch"
                      class="rotate"
                      height="12px"
                      src="@/assets/images/loading.svg"
                      alt=""
                    />
                    Save
                  </button>
                </div>

                <div class="wrapper">
                  <img
                    style="cursor: pointer"
                    class="right-mar"
                    src="@/assets/images/share.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -20px" class="tooltip">Share</div>
                </div>
              </div>

              <pre class="pre-text" v-html="summary"></pre>
            </div>
          </div>
        </div>

        <div v-if="filteredArticles.length && !loading" class="divider">
          <p class="divider-text">News Clips</p>
        </div>

        <div style="width: 50%" v-if="loading">
          <div class="article-preview-skeleton shimmer">
            <div class="content">
              <div class="title"></div>
              <div class="meta"></div>
              <div class="excerpt"></div>
              <div class="skeleton-footer"></div>
            </div>
            <div class="thumbnail"></div>
          </div>
          <div class="article-preview-skeleton shimmer">
            <div class="content">
              <div class="title"></div>
              <div class="meta"></div>
              <div class="excerpt"></div>
              <div class="skeleton-footer"></div>
            </div>
            <div class="thumbnail"></div>
          </div>
          <div class="article-preview-skeleton shimmer">
            <div class="content">
              <div class="title"></div>
              <div class="meta"></div>
              <div class="excerpt"></div>
              <div class="skeleton-footer"></div>
            </div>
            <div class="thumbnail"></div>
          </div>
        </div>

        <div v-else class="clips-container">
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
                    <p class="article-preview">
                      {{ article.description }}
                    </p>
                  </div>

                  <div @click="goToArticle(article.url)">
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
                    <button
                      :disabled="articleSummaryLoading || loading || summaryLoading || savingSearch"
                      class="tertiary-button"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                        <path
                          d="M17.5 1.25a.5.5 0 0 1 1 0v2.5H21a.5.5 0 0 1 0 1h-2.5v2.5a.5.5 0 0 1-1 0v-2.5H15a.5.5 0 0 1 0-1h2.5v-2.5zm-11 4.5a1 1 0 0 1 1-1H11a.5.5 0 0 0 0-1H7.5a2 2 0 0 0-2 2v14a.5.5 0 0 0 .8.4l5.7-4.4 5.7 4.4a.5.5 0 0 0 .8-.4v-8.5a.5.5 0 0 0-1 0v7.48l-5.2-4a.5.5 0 0 0-.6 0l-5.2 4V5.75z"
                          fill="#000"
                        ></path>
                      </svg>
                      Tag
                    </button>

                    <button
                      v-if="!articleSummaries[article.url]"
                      @click="getArticleSummary(article.url)"
                      class="tertiary-button"
                      :disabled="articleSummaryLoading || loading || summaryLoading || savingSearch"
                    >
                      <img
                        v-if="articleSummaryLoading && loadingUrl === article.url"
                        class="rotate"
                        height="14px"
                        src="@/assets/images/loading.svg"
                        alt=""
                      />
                      <img
                        v-else-if="!articleSummaryLoading"
                        src="@/assets/images/sparkles-thin.svg"
                        height="14px"
                        alt=""
                      />
                      Summarize
                    </button>

                    <img
                      v-else
                      src="@/assets/images/sparkle.svg"
                      class="right-arrow-footer blue-icon"
                    />
                  </div>
                </div>
                <div v-if="articleSummaries[article.url]">
                  <pre v-html="articleSummaries[article.url]" class="pre-text blue-bg"></pre>
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
      type: String,
    },
  },
  data() {
    return {
      isTyping: false,
      textIndex: 0,
      typedMessage: '',
      savingSearch: false,
      searchMessages: [
        'University of Michigan no sports related mentions',
        'Walmart no stock related mentions',
        "Boston Children's no ER related stories",
        'Stranger Things and Netflix',
        'The Bear and Hulu, reviews or ratings',
        'Barbie or Oppenheimer movie debut',
        'Sun bear and China Zoo',
        'Cancer research and new treatment',
        '2024 Tesla Model S',
        'Madden NFL 24 reviews',
        'Cybertruck vs Rivian',
        'Rent prices in Manhattan',
        'Best new electric cars',
        'Climate change and wildlife',
        'AI only in Techcrunch sources',
        'Authors and Lawrence Bonk',
        'All stories about or written by Ron Miller',
        'Rutgers University broad search',
        'Beyond meat broad search',
        'Beyond burger or sausage or meat',
        'Impossible burger, including their products',
      ],
      starterNum: 0,
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
      booleanString: null,
      newSummary: false,
      addingPrompt: false,
      addingSources: false,
      articleSummaries: {},
      loadingUrl: null,
      articleSummaryLoading: false,
    }
  },
  created() {},
  watch: {
    typedMessage: 'changeIndex',
    currentSearch(newVal, oldVal) {
      if (newVal.id !== (oldVal ? oldVal.id : null)) {
        this.setSearch(newVal)
      }
    },
  },
  mounted() {
    // this.updateMessage()
  },
  methods: {
    setSearch(search) {
      this.newSearch = search.input_text
      this.newTemplate = search.instructions
      this.generateNewSearch()
    },
    changeIndex() {
      setTimeout(() => {
        this.isTyping = false
        this.typedMessage = ''
      }, 5750)
      setTimeout(() => {
        this.updateMessage()
      }, 5850)
    },
    updateMessage() {
      console.log('here')
      this.textIndex = Math.floor(Math.random() * this.searchMessages.length)
      this.isTyping = true
      this.typedMessage = this.searchMessages[this.textIndex]
    },
    scrollToTop() {
      setTimeout(() => {
        const loadedContent = this.$refs.loadedContent
        loadedContent.scrollTop = loadedContent.scrollHeight
      }, 200)
    },
    removeSource() {
      this.additionalSources = ''
      this.addingSources = !this.addingSources
    },
    removePrompt() {
      this.newTemplate = ''
      this.addingPrompt = !this.addingPrompt
    },
    toggleAddPrompt() {
      this.addingPrompt = !this.addingPrompt
    },
    toggleAddSource() {
      this.addingSources = !this.addingSources
    },
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
      if (!this.newSearch || this.newSearch.length < 3) {
        return
      }
      this.loading = true
      this.summaryLoading = true
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      try {
        this.getClips(this.newSearch).then((response) => {
          this.getSummary(this.filteredArticles, this.newTemplate)
        })
      } catch (e) {
        console.log(e)
      }
      this.closeRegenModal()
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
    async createSearch() {
      this.savingSearch = true
      try {
        const response = await Comms.api
          .createSearch({
            name: this.newSearch.slice(0, 60),
            input_text: this.newSearch,
            search_boolean: this.booleanString,
            instructions: this.newTemplate,
          })
          .then((response) => {
            console.log(response)
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.savingSearch = false
        this.$store.dispatch('getSearches')
      }
    },
    async getClips() {
      try {
        await Comms.api
          .getClips({
            search: this.newSearch,
            user_id: this.user.id,
          })
          .then((response) => {
            console.log(response)
            this.filteredArticles = response.articles
            this.booleanString = response.string
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.loading = false
      }
    },
    getArticleDescriptions(articles) {
      return articles.map((a) => a.content)
    },
    async getSummary(clips, instructions = '') {
      const allClips = this.getArticleDescriptions(clips)
      this.summaryLoading = true
      try {
        await Comms.api
          .getSummary({
            clips: allClips,
            search: this.newSearch,
            instructions: instructions,
          })
          .then((response) => {
            console.log(response)
            this.summary = response.summary
          })
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
        this.scrollToTop()
      }
    },
    async getArticleSummary(url, instructions = null) {
      this.articleSummaryLoading = true
      this.loadingUrl = url
      try {
        await Comms.api
          .getArticleSummary({
            url: url,
            search: this.newSearch,
            instructions: instructions,
          })
          .then((response) => {
            this.articleSummaries[url] = response.summary
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.articleSummaryLoading = false
        this.loadingUrl = null
      }
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
      window.open(link, '_blank')
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
    user() {
      return this.$store.state.user
    },
    currentSearch() {
      return this.$store.state.currentSearch
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        // el.style.overflow = 'scro'

        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', adjustTextareaHeight)
        adjustTextareaHeight()
      },
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

@keyframes deleting {
  from {
    width: 100%;
  }
  to {
    width: 0;
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

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.typed-deleted {
  overflow: hidden;
  white-space: nowrap;
  width: 0;
  animation: typing 2.5s steps(30, end) forwards, deleting 2.75s steps(30, end) 2.75s forwards,
    blinking 1s infinite;
  border-right: 1px solid;
}

.typed {
  overflow: hidden;
  white-space: nowrap;
  width: 0;
  animation: typing 2s steps(30, end) forwards, blinking 1s infinite;
  border-right: 1px solid;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.neg-l-mar {
  margin-left: -1rem;
}

.neg-lmar {
  margin-left: -1rem;
}

.summary-load-text {
  font-family: $thin-font-family;
  font-size: 14px;
  margin-left: 8px;
}

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;
}

.invert {
  filter: invert(70%);
}

.loader-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin-left: -48px;
  margin-bottom: 16px;
}

.loader-row {
  border-radius: 6px;
  padding: 0.25rem 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 6px;
  padding: 1.5rem 0.75rem;
}
.mar-top {
  margin-top: 24px;
}

.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}

.search-text {
  color: $dark-black-blue;
  font-weight: 900;
  color: #6b6b6b;
}

button:disabled {
  background-color: $off-white !important;
  border: 1px solid rgba(0, 0, 0, 0.2) !important;
  cursor: not-allowed !important;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.tertiary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
  svg,
  img {
    // filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.secondary-button {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  background-color: white;
  padding: 8px 12px;
  img {
    filter: invert(25%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;
}
.center {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
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
.s-padding {
  padding: 0 0.25rem !important;
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
  font-family: $base-font-family;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
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
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0;
}

.blue-bg {
  background-color: $white-blue;
  padding: 16px;
  border-radius: 4px;
}
.blue-icon {
  filter: invert(92%) sepia(53%) saturate(2928%) hue-rotate(178deg) brightness(72%) contrast(96%);
}

.right-mar {
  margin-right: 12px;
}
.loaded-content {
  width: 100%;
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
.remove {
  color: #6b6b6b;
  cursor: pointer;
  border-radius: 100%;
  padding: 1px 6px;
  margin-right: -4px;
  font-family: $thin-font-family;
  &:hover {
    color: $coral;
    background-color: $light-red;
  }
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

.divider {
  position: relative;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}

.divider-text {
  position: absolute;
  top: -32px;
  left: 44%;
  z-index: 20;
  background-color: white;
  padding: 4px 16px;
  border-radius: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.summaries-container {
  display: flex;
  justify-content: flex-start;
  width: 100%;
  margin-bottom: 0;
  background-color: $off-white;
  padding-top: 0;
  padding-bottom: 40px;
}
.clips-container {
  display: flex;
  justify-content: flex-start;
  width: 100%;
  // margin-top: 40px;
}
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
  padding-top: 32px;
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
}

.title-container {
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}

.title-bar {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 24px 0 24px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.sub-text {
  color: $light-gray-blue;
  margin: 8px 0 0 0;
  font-size: 14px;
  font-weight: bold;
  font-family: $thin-font-family;
  span {
    font-weight: normal;
    word-wrap: break-word;
  }
}

.no-text-margin {
  margin: 0;
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

  &:hover {
    opacity: 0.7;
  }
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
  cursor: pointer;

  &:hover {
    color: #6b6b6b;
  }
}

.article-preview {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  height: 68px;
  line-height: 24px;
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
}
.right-arrow-footer {
  padding: 2px 0;
  height: 20px;
  margin-left: 1rem;
  cursor: text;
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
  padding: 1rem;
  font-family: $base-font-family;
}
.regen-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: 0;
  padding-top: 12px;
  display: flex;
  justify-content: flex-end;
}
.blue-border-button {
  @include dark-blue-border-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
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
  margin-top: 84px;
}
.regen-container {
  height: 500px;
  position: relative;
  overflow-y: scroll;
}
.message-text {
  font-family: $base-font-family;
  word-wrap: break-word;
  white-space: pre-wrap;
}
@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.shimmer {
  display: inline-block;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
}

.loadingText {
}

.article-preview-skeleton {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px;
  border-radius: 4px;
  margin-top: 16px;
  width: 100%;
}

.summary-preview-skeleton {
  width: 100%;
  min-width: 400px;
  padding: 8px 20px 36px 20px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
}

.thumbnail {
  height: 112px;
  width: 116px;
  background-color: #f2f2f2;
  border-radius: 6px;
  margin-left: 16px;
}

.content {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.title {
  width: 100%;
  min-width: 400px;
  height: 24px;
  background-color: #f2f2f2;
  margin-bottom: 8px;
  border-radius: 6px;
}
.title-wide {
  width: 100%;
  height: 28px;
  background-color: $dark-black-blue;
  margin-bottom: 12px;
  border-radius: 12px;
}

.meta {
  width: 100%;
  min-width: 399px;
  height: 8px;
  background-color: #f2f2f2;
  border-radius: 6px;
  margin-bottom: 8px;
}

.blue-logo {
  filter: brightness(0%) invert(26%) sepia(16%) saturate(936%) hue-rotate(162deg) brightness(93%)
    contrast(97%);
}

.meta-wide {
  width: 100%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shorter {
  width: 80%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}

.skeleton-bar {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 16px 0;
}

.skeleton-button {
  height: 20px;
  width: 100px;
  margin-right: 16px;
  background-color: #f2f2f2;
  border-radius: 6px;
}

.skeleton-icon {
  border-radius: 50%;
  height: 20px;
  width: 20px;
  background-color: #f2f2f2;
}

.excerpt {
  width: 100%;
  min-width: 399px;
  height: 8px;
  background-color: #f2f2f2;
  border-radius: 6px;
}
.excerpt-wide {
  width: 100%;
  height: 8px;
  background-color: #f2f2f2;
  margin-top: 16px;
  border-radius: 6px;
}

.skeleton-footer {
  width: 150px;
  height: 12px;
  margin-top: 32px;
  background-color: #f2f2f2;
  border-radius: 6px;
}

.wrapper {
  display: flex;
  align-items: center;
  // background-color: red;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -20px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}
</style>