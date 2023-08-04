<template>
  <div class="main-content">
    <div class="left-content">
      <div>
        <div @click="getClips" class="gray-background">
          <div
            class="toggle-container"
            :class="summaryChat === 'SUMMARY' ? 'active' : ''"
            @click="changeSummaryChat('SUMMARY')"
          >
            <p>Summary</p>
          </div>
          <div
            class="toggle-container"
            :class="summaryChat === 'CHAT' ? 'active' : ''"
            @click="changeSummaryChat('CHAT')"
          >
            <p>Chat</p>
          </div>
        </div>
        <div v-if="summaryChat === 'SUMMARY'">
          <p class="small-title-text"><img src="@/assets/images/sparkles-round.svg" />Summary</p>
        </div>
        <div v-else>
          <p class="small-title-text"><img src="@/assets/images/sparkles-round.svg" />Chat</p>
        </div>
      </div>
      <div v-if="summaryChat === 'SUMMARY'">
        <div v-if="!summary" class="summary-buttons-container">
          <button class="summary-button wide" @click="getSummary(filteredArticles)"><img src="@/assets/images/sparkles-round.svg" />Generate Summary</button>
        </div>
        <div v-else>
          <div class="highlights-summary-container">
            <pre v-html="summary" class="message-text" />
          </div>
          <div v-if="regenSummary">
            <div class="provide-instructions">
              <span>Provide Instructions:</span>
              <img
                class="back-arrow"
                src="@/assets/images/arrow-small-left.svg"
                @click="changeRegen"
              />
            </div>
            <div class="chat-border">
              <div class="input-container">
                <input v-model="message" placeholder="Provide Instructions..." />
                <font-awesome-icon
                  :class="{ invert: !message.length }"
                  class="gray"
                  style="height: 14px; cursor: pointer"
                  icon="fa-regular fa-paper-plane"
                  @click="regenNewSummary"
                />
              </div>
            </div>
          </div>
          <div v-else-if="newSummary">
            <div class="provide-instructions">
              <span>Selected: {{ selectedArticles.length }}</span>
              <img
                class="back-arrow"
                src="@/assets/images/arrow-small-left.svg"
                @click="changeNew"
              />
            </div>
            <div>
              <div v-if="!selectedArticles.length" class="summarize-disabled">
                Select the clips you'd like to summarize
              </div>
              <div v-else class="summarize" @click="saveSelectedArticles">Summarize</div>
            </div>
          </div>
          <div v-else class="summary-buttons-container">
            <button @click="changeRegen" class="summary-button">
              <img src="@/assets/images/sparkles-round.svg" />Regenerate
            </button>
            <button @click="changeNew" class="summary-button dark-button">
              <img src="@/assets/images/sparkles-round.svg" />New Summary
            </button>
          </div>
        </div>
      </div>
      <div v-else-if="summaryChat === 'CHAT'" class="chat-container">
        <div class="margin-top chat-window" ref="chatWindow"></div>
        <div class="bottom">
          <div class="chat-button-container">
            <div class="chat-button">Summarize</div>
            <div class="chat-button">Generate</div>
            <div class="chat-button">Ask Question</div>
          </div>
          <div class="chat-border">
            <div class="input-container">
              <input v-model="message" placeholder="What would you like to do..." />
              <font-awesome-icon
                :class="{ invert: !message }"
                class="gray"
                style="height: 14px; cursor: pointer"
                icon="fa-regular fa-paper-plane"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="right-content">
      <div class="updated-time"></div>
      <div class="search-results">
        <div>
          <p>Results: {{ filteredArticles.length }}</p>
        </div>
        <div class="search-bar">
          <img class="search" src="@/assets/images/search-round.svg" />
          <input @input="searchTitles" type="search" :placeholder="`Search`" v-model="filterText" />
        </div>
      </div>
      <div class="card-container">
        <div v-if="loading">....</div>

        <div v-else>
          <div v-for="article in filteredArticles" :key="article.id" class="">
            <div class="card" @click="selectArticle(article)">
              <div class="display-flex">
                <div class="">
                  <div class="card-top-left">
                    <img :src="article.icon" />
                    <span>{{ article.source.name }}</span>
                  </div>
                  <h3 class="article-title" @click="goToArticle(article.url)">
                    {{ article.title }}
                  </h3>
                  <h4 class="article-preview">{{ article.description }}</h4>
                </div>
                <div @click="goToArticle(article.link)">
                  <img :src="article.urlToImage" class="cover-photo" />
                </div>
              </div>
              <div class="card-footer">
                <div class="author-time">
                  <span>{{ article.publishedAt }}</span>
                  <span class="divier-dot">.</span>
                  <span>{{ article.author }}</span>
                </div>
                <div class="footer-icon-container">
                  <div v-if="newSummary" class="">
                    <input type="checkbox" @click="addRemoveSelectedArticles(article)" />
                  </div>
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
    </div>
  </div>
</template>
<script>
import ChatTextBox from '../Chat/ChatTextBox.vue'
import Comms from '@/services/comms'

export default {
  name: 'SummariesMainContent',
  components: {
    ChatTextBox,
  },
  data() {
    return {
      loading: false,
      summary: null,
      articles: [],
      summaryChat: 'SUMMARY',
      filterText: '',
      message: '',
      regenSummary: false,
      newSummary: false,
      selectedArticles: [],
      filteredArticles: [],
      actions: [
        {
          name: 'Summarize',
          value: 'Summarize...',
        },
        { name: 'Generate', value: 'Generate...' },
        { name: 'Ask Managr', value: 'Ask managr... ' },
      ],
    }
  },
  watch: {},
  created() {},
  methods: {
    async getClips() {
      this.loading = true
      try {
        await Comms.api
          .getClips({
            search: 'Houston rockets',
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
      console.log('articles', articles)
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
        console.log('data', data)
        const res = await Comms.api.getSummary(data)
        this.summary = res.summary
      } catch(e) {
        console.log('Error in getSummary', e)
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
      const existingArticle = this.selectedArticles.filter((ar) => ar.id === article.id)[0]
      if (existingArticle) {
        this.selectedArticles = this.selectedArticles.filter((ar) => ar.id !== article.id)
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
  min-height: 88vh;
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
  width: 29vw;
}
.right-content {
  width: 38vw;
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
.dark-button {
  @include dark-blue-button();
  padding: 8px 16px;
  img {
    // filter: invert(99%);
    filter: invert(81%) sepia(38%) saturate(738%) hue-rotate(349deg) brightness(95%) contrast(88%);
  }
}
.wide {
  width: 90%;
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
  font-size: 16px;
}
.dot {
  height: 8px;
  width: 8px;
  margin: 0.275rem 0.5rem 0 0;
}
.overall {
  font-size: 16px;
}
.highlight-point {
  font-size: 14px;
  // word-spacing: 1.15px;
  line-height: 1.5;
}
.small-title-text {
  font-size: 14px;
  color: $light-gray-blue;
  img {
    height: 12px;
    margin-right: 0.5rem;
    filter: invert(81%) sepia(38%) saturate(738%) hue-rotate(349deg) brightness(95%) contrast(88%);
    // filter: invert(63%) sepia(9%) saturate(735%) hue-rotate(200deg) brightness(95%) contrast(92%);
  }
}
.chat-container {
  width: 100%;
  height: 75vh;
  overflow-y: auto;
}
.chat-window {
  min-height: 63vh;
}
.message-text {
  font-family: $base-font-family;
  word-wrap: break-word;
  white-space: pre-wrap;
  padding: 0;
  margin: 0;
}
.message-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin: 0;
  width: 100%;
  padding: 0 1.5rem;

  p {
    padding: 0;
    margin: 0;
  }

  &:hover {
    background-color: $off-white !important;
  }
}

.message-container:first-of-type {
  padding-top: 0.5rem;
}
.margin-top {
  // margin-top: 4rem;
  // height: 96%;
  // overflow-y: auto;
}
.container-padding {
  border-radius: 6px;
  padding: 0.5rem;
}

.ai-text-container {
  overflow: scroll;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  padding: 0 0.75rem;
  line-height: 1.75;
  position: relative;

  &:hover {
    background-color: $off-white !important;
  }
}

.text-container {
  overflow: scroll;
  padding: 0.25rem;
  margin: 0;
  line-height: 1.75;
}

.images {
  padding: 0;
  margin: 0 0.5rem 0 0;
}

.bottom {
  position: sticky;
  bottom: 0;
  left: 0;
}

.bottom-right {
  position: absolute;
  bottom: 0;
  right: 0;
}

.avatar {
  background-color: $purple;
  color: white;
  width: 22px;
  height: 22px;
  margin-right: 0.2rem;
  margin-top: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.title-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-family: $base-font-family;
  background-color: white;

  h4,
  p {
    margin: 0;
    padding: 0.5rem;
    width: fit-content;
    // outline: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    // background-color: white;
    font-size: 12px;
    letter-spacing: 0.4px;

    span {
      color: $light-gray-blue;
    }
  }
}

@media (max-width: 768px) {
  .chat-container {
    font-size: 14px;
  }
}

.green-filter {
  filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
    contrast(82%);
}
.gold-filter {
  filter: invert(89%) sepia(43%) saturate(4130%) hue-rotate(323deg) brightness(90%) contrast(87%);
  animation: shimmer 2s;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/200% 100%;
}

.invert {
  filter: invert(95%);
}

.green {
  background-color: $dark-green !important;
  color: white !important;
  border: 1px solid $dark-green !important;
}

.loader-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin-bottom: 1.5rem;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  // background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.75rem 0.75rem;
}

// .dot {
//   width: 4px;
//   height: 4px;
//   margin: 0 5px;
//   background: rgb(97, 96, 96);
//   border-radius: 50%;
//   animation: bounce 1.2s infinite ease-in-out;
// }

// .dot:nth-child(2) {
//   animation-delay: -0.4s;
// }

// .dot:nth-child(3) {
//   animation-delay: -0.2s;
// }

.col-start {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.generate-container {
  padding: 0 1rem 0.5rem 4.5rem;
  background-color: white;
  width: 100%;
}

.generate-button {
  @include chat-button();
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.5rem;
  img {
    margin-right: 0.5rem;
  }
}

.content-button {
  @include chat-button();
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  margin-right: 0.5rem;
  svg {
    margin-right: 0.5rem;
  }
}

.small-button {
  @include chat-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-radius: 5px;
  font-size: 12px;
  padding: 0.35rem;
  margin-left: 1rem;
  font-weight: normal;

  img {
    margin: 0;
    margin-right: 0.5rem;
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

.go-back {
  position: absolute;
  right: 0.5rem;
  top: -1.75rem;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.back {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $coral;
  width: 20px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 0.5rem;
  margin-right: 2px;
  font-size: 11px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }

  img {
    transform: rotate(180deg);
  }
}

.pointer {
  cursor: pointer;
}
// @keyframes typing {
//   from {
//     width: 0;
//   }
//   to {
//     width: 100%;
//   }
// }

// @keyframes blinking {
//   0% {
//     border-right-color: transparent;
//   }
//   50% {
//     border-right-color: rgb(66, 65, 65);
//   }
//   100% {
//     border-right-color: transparent;
//   }
// }

// .typed {
//   overflow: hidden;
//   white-space: nowrap;
//   width: 0;
//   animation: typing 1.5s steps(30, end) forwards, blinking 1s infinite;
//   border-right: 1px solid;
// }
.chat-button-container {
  display: flex;
  justify-content: center;
  margin-bottom: 0.5rem;
}
.chat-button {
  @include secondary-button();
  // width: 6rem;
  padding: 0.5rem 1.2rem;
  margin: 0 0.5rem;
}
.chat-border {
  background-color: $silver;
  padding: 0.25rem;
  border-radius: 4px;
}
.input-container {
  background-color: $white;
  padding: 0.5rem;
  border-radius: 4px;
  box-shadow: 0 0 3px $very-light-gray;
  input {
    border: none;
    outline: none;
    width: 95%;
  }
}
.provide-instructions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 1rem 0;
  font-size: 14px;
}
.back-arrow {
  height: 20px;
  cursor: pointer;
}
.gray {
  color: rgb(82, 80, 80);
}
.summarize {
  @include gray-text-button();
}
.summarize-disabled {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  border: 1px solid $soft-gray;
  color: $base-gray;
  font-size: 12px;
  transition: all 0.3s;
}
</style>