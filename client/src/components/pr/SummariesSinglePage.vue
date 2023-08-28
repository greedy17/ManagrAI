<template>
  <div ref="loadedContent" class="main-content">
    <!-- <div class="suggestions" v-if="!selectedSearch">
      <img class="invert-dark-blue" src="@/assets/images/lightbulb.svg" height="18px" alt="" />
    </div> -->
    <Modal v-if="regenModal" class="regen-modal">
      <div class="regen-container">
        <div class="regen-header">
          <div>
            <h4 class="regen-header-title">Regenerate Search</h4>
            <p v-if="!searchSaved && mainView !== 'website'" class="regen-header-subtitle">
              Create a new search using conversational AI
            </p>
            <p v-else-if="mainView === 'website'" class="regen-header-subtitle">
              Create a new summary
            </p>
            <p class="regen-header-subtitle" v-else>Create a new summary</p>
          </div>
          <div class="pointer" @click="closeRegenModal"><small>X</small></div>
        </div>
        <div class="regen-body">
          <div v-if="!searchSaved">
            <div>
              <h5 class="regen-body-title">Search term</h5>
              <!-- <span class="regen-header-subtitle"
                >Use conversation text. AI will convert it to a boolean.</span
              > -->
            </div>
            <textarea v-autoresize v-model="newSearch" class="regen-body-text" />
          </div>
          <div v-if="mainView !== 'website'">
            <div>
              <h5 class="regen-body-title">
                Summary Instructions <span class="regen-header-subtitle">(optional)</span>
              </h5>
            </div>
            <textarea v-autoresize v-model="newTemplate" class="regen-body-text" />
          </div>

          <div v-else>
            <div>
              <h5 class="regen-body-title">
                Summary instructions <span class="regen-header-subtitle"></span>
              </h5>
            </div>
            <textarea v-autoresize v-model="newTemplate" class="regen-body-text" />
          </div>
        </div>
        <div class="regen-footer">
          <div></div>
          <div class="row">
            <div class="cancel-button" @click="closeRegenModal">Cancel</div>
            <div class="save-button" @click="generateNewSearch(null)">Submit</div>
          </div>
        </div>
      </div>
    </Modal>

    <div class="floating-action-bar">
      <div class="main-slot">
        <img src="@/assets/images/share.svg" height="10px" alt="" />
      </div>

      <div class="slot-container">
        <!-- <img src="" alt=""> -->
        <div class="empty-slot"></div>
        <div class="empty-slot"></div>
        <div class="empty-slot"></div>
      </div>
    </div>

    <div class="center column" :class="{ fullHeight: showingDropdown }" v-if="page === 'SUMMARIES'">
      <div v-if="!selectedSearch" class="switcher">
        <div
          @click="switchMainView('news')"
          :class="{ activeswitch: mainView === 'news' }"
          class="switch-item"
        >
          <img src="@/assets/images/memo.svg" height="12px" alt="" />
          News
        </div>
        <div
          @click="switchMainView('social')"
          :class="{ activeswitch: mainView === 'social' }"
          class="switch-item"
        >
          <img src="@/assets/images/comment.svg" height="12px" alt="" />
          Social
        </div>
        <div
          @click="switchMainView('website')"
          :class="{ activeswitch: mainView === 'website' }"
          class="switch-item"
        >
          <img src="@/assets/images/globe.svg" height="18px" alt="" />
          URL
        </div>
      </div>

      <div class="no-content" v-if="!selectedSearch">
        <div class="title-row">
          <div class="row" v-if="!newSearch">
            <p class="typed">
              {{
                mainView === 'social'
                  ? 'Generate a summary from X (formally Twitter)'
                  : mainView === 'website'
                  ? 'Generate a summary from a news article'
                  : 'Generate a news summary from over 1 million sites'
              }}
            </p>
          </div>

          <p v-else>
            Summarize coverage for <span class="search-text">"{{ newSearch }}"</span>
          </p>
        </div>
        <div>
          <div style="margin-bottom: 30px" class="input-container" v-clickOutsideMenu>
            <div class="input-row">
              <div style="border-right: none" class="main-text">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M4.1 11.06a6.95 6.95 0 1 1 13.9 0 6.95 6.95 0 0 1-13.9 0zm6.94-8.05a8.05 8.05 0 1 0 5.13 14.26l3.75 3.75a.56.56 0 1 0 .8-.79l-3.74-3.73A8.05 8.05 0 0 0 11.04 3v.01z"
                    fill="currentColor"
                  ></path>
                </svg>
              </div>
              <!-- @keydown.enter.exact.prevent="generateNewSearch(null)" -->
              <input
                @click.stop
                id="search-input"
                class="area-input"
                placeholder="Search term..."
                @focus="showDropdown"
                autocomplete="off"
                v-model="newSearch"
              />
              <!-- <img
                :class="{ invert: !newSearch }"
                src="@/assets/images/paper-plane.svg"
                height="14px"
                alt=""
                @click="generateNewSearch(null)"
                class="pointer"
              /> -->
            </div>

            <div v-if="showingDropdown" class="dropdown">
              <small style="padding-top: 8px" class="gray-text">Example Searches</small>
              <div
                @click="addSuggestion(suggestion)"
                class="dropdown-item"
                v-for="(suggestion, i) in filteredSuggestions"
                :key="i"
              >
                <p>
                  {{ suggestion }}
                </p>
              </div>
            </div>
          </div>

          <div style="margin-top: 1rem" class="input-container" v-clickOutsidePromptMenu>
            <div class="input-row-start">
              <div class="main-text">
                <img
                  style="margin-right: 8px"
                  src="@/assets/images/sparkles-thin.svg"
                  height="16px"
                />
              </div>
              <textarea
                @focus="showPromptDropdown"
                class="area-input"
                placeholder="Custom summary instructions... (Optional)"
                v-model="newTemplate"
                v-autoresize
              />
              <!-- <small @click="removePrompt" class="remove">X</small> -->
            </div>

            <div v-if="showingPromptDropdown" class="dropdown">
              <small style="padding-top: 8px" class="gray-text">Example Prompts</small>
              <div
                class="dropdown-item"
                v-for="(suggestion, i) in filteredPromptSuggestions"
                :key="i"
                @click="addPromptSuggestion(suggestion)"
              >
                <p>
                  {{ suggestion }}
                </p>
              </div>
            </div>
          </div>

          <div v-if="mainView === 'website'" style="margin-top: 2rem" class="input-container">
            <div class="input-row">
              <div class="main-text">
                <img src="@/assets/images/globe.svg" height="20px" />
              </div>
              <input class="area-input" placeholder="Article URL..." v-model="additionalSources" />
              <!-- <small @click="removeSource" class="remove">X</small> -->
            </div>
          </div>

          <div class="center mar-top pad-btm">
            <!-- <button @click="toggleAddPrompt" v-if="!addingPrompt" class="secondary-button">
              Custom Prompt
            </button> -->
            <!-- <button @click="toggleAddSource" v-if="!addingSources" class="secondary-button">
              Article Summary
            </button> -->

            <button
              v-if="mainView !== 'website'"
              @click="generateNewSearch(null)"
              :disabled="!newSearch"
              class="primary-button"
            >
              Generate Summary
            </button>

            <button
              v-else
              @click="getSourceSummary()"
              :disabled="!additionalSources || !newSearch"
              class="primary-button"
            >
              Generate Summary
            </button>
          </div>
        </div>
      </div>
      <div :class="{ wbbackground: summaryLoading }" v-else class="loaded-content">
        <div class="loader-bg" :class="{ 'neg-lmar': !loading }" v-if="summaryLoading">
          <div :class="{ 'left-mar': loading }" class="row">
            <p class="summary-load-text">Generating Summary...</p>
          </div>

          <div :class="{ 'neg-l-mar': !loading }" class="summary-preview-skeleton shimmer">
            <div class="content">
              <div class="meta-wide"></div>
              <div class="meta-shorter"></div>
              <div class="meta-shortest"></div>
              <!-- <div class="meta-small"></div> -->
            </div>
          </div>
        </div>
        <div v-else class="summaries-container">
          <Transition name="slide-fade">
            <div v-if="showUpdateBanner" class="templates">
              <p>Search saved successfully!</p>
            </div>
          </Transition>
          <div class="content-width">
            <div class="news-container">
              <div class="title-container">
                <div @click="resetSearch" class="back">
                  <img src="@/assets/images/back.svg" height="18px" width="18px" alt="" />
                </div>
                <h1 class="no-text-margin">
                  {{ selectedSearch.search }}
                </h1>
                <p v-if="mainView !== 'website'" class="sub-text">
                  AI generated search: <span>{{ booleanString }}</span>
                </p>

                <p v-else class="sub-text">
                  Article summary: <span>{{ additionalSources }}</span>
                </p>
              </div>
              <div class="title-bar">
                <div v-if="!showSaveName" class="row">
                  <button
                    :disabled="articleSummaryLoading || loading || summaryLoading || savingSearch"
                    @click="openRegenModal"
                    class="secondary-button"
                  >
                    {{
                      filteredArticles.length || mainView === 'website'
                        ? 'Regenerate'
                        : tweets.length
                        ? 'Regenerate'
                        : 'New Search'
                    }}
                  </button>
                  <button
                    @click="toggleSaveName"
                    v-if="filteredArticles.length || tweets.length"
                    :disabled="
                      articleSummaryLoading ||
                      loading ||
                      summaryLoading ||
                      savingSearch ||
                      searchSaved ||
                      mainView === 'website'
                    "
                    class="primary-button"
                  >
                    <img
                      v-if="savingSearch"
                      class="rotate"
                      height="12px"
                      src="@/assets/images/loading.svg"
                      alt=""
                    />
                    {{ savingSearch ? 'Saving' : 'Save' }}
                  </button>
                </div>

                <div v-else class="row">
                  <input
                    autofocus
                    class="area-input-outline"
                    placeholder="Name your search"
                    v-model="searchName"
                  />

                  <button
                    @click="createSearch"
                    :disabled="
                      articleSummaryLoading ||
                      loading ||
                      summaryLoading ||
                      savingSearch ||
                      searchSaved
                    "
                    class="primary-button"
                  >
                    Save
                  </button>
                </div>

                <div @click="copyText" class="wrapper">
                  <img
                    style="cursor: pointer"
                    class="right-mar img-highlight"
                    src="@/assets/images/clipboard.svg"
                    height="14px"
                    alt=""
                  />
                  <div style="margin-left: -20px" class="tooltip">{{ copyTip }}</div>
                </div>
              </div>

              <pre class="pre-text" v-html="summary"></pre>
            </div>
          </div>
        </div>

        <div
          v-if="
            ((filteredArticles && filteredArticles.length) || (tweets && tweets.length)) && !loading
          "
          class="divider"
        >
          <p class="divider-text">
            {{
              mainView === 'news'
                ? 'News Clips'
                : mainView === 'website'
                ? 'Website'
                : 'Social Media'
            }}
          </p>
        </div>

        <div style="background-color: white" class="loaded-content" v-if="loading">
          <div style="width: 50%">
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
        </div>

        <div v-else class="clips-container">
          <div class="content-width" v-if="mainView === 'social' && tweets.length">
            <div class="news-container-med" v-for="(tweet, i) in tweets" :key="i">
              <div class="news-card-medium">
                <header class="neg-margin">
                  <div class="card-row-med">
                    <img :src="tweet.user.profile_image_url" />
                    <h1 @click="openTweet(tweet.user.username, tweet.id)" class="article-title">
                      {{ tweet.user.name }}
                    </h1>
                    <svg
                      v-if="tweet.user.verified"
                      width="16"
                      height="16"
                      viewBox="0 0 22 22"
                      aria-label="Verified account"
                      role="img"
                      class="twitter-blue"
                      data-testid="icon-verified"
                    >
                      <g>
                        <path
                          d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z"
                        ></path>
                      </g>
                    </svg>
                  </div>
                </header>

                <p class="article-preview">{{ tweet.text }}</p>
                <div v-if="tweet.attachments">
                  <div
                    style="margin-bottom: 16px"
                    v-for="media in tweetMedia"
                    :key="media.media_key"
                  >
                    <div v-if="media.media_key === tweet.attachments.media_keys[0]">
                      <img
                        v-if="media.type === 'photo'"
                        :src="media.url"
                        class="cover-photo-no-l-margin"
                        alt=""
                      />

                      <video
                        style="margin-top: 1rem"
                        v-else-if="media.type === 'video'"
                        width="400"
                        controls
                      >
                        <source :src="media.variants[1].url" type="video/mp4" />
                      </video>

                      <video
                        style="margin-top: 1rem"
                        v-else-if="media.type === 'animated_gif'"
                        width="400"
                        autoplay
                        loop
                        muted
                        playsinline
                      >
                        <source :src="media.variants[0].url" type="video/mp4" />
                      </video>
                    </div>
                  </div>
                </div>

                <div class="card-footer">
                  <div class="author-time">
                    <span class="author">{{ '@' + tweet.user.username }}</span>
                    <span class="divier-dot">.</span>
                    <small class="bold-text"
                      >{{ formatNumber(tweet.user.public_metrics.followers_count) }}
                      <span>Followers</span>
                    </small>
                    <span class="divier-dot">.</span>
                    <span class="off-gray">{{ getTimeDifferenceInMinutes(tweet.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="content-width" v-else-if="mainView === 'social' && tweetError">
            <div class="news-container">
              <div class="no-results">
                <p>{{ tweetError }}</p>
              </div>
            </div>
          </div>
          <div v-else-if="mainView === 'news'" class="content-width">
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
                    <!-- <button
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
                    </button> -->

                    <button
                      v-if="!articleSummaries[article.url]"
                      @click="getArticleSummary(article.url)"
                      class="tertiary-button"
                      style="margin: 0"
                      :disabled="articleSummaryLoading || loading || summaryLoading || savingSearch"
                    >
                      <img
                        v-if="articleSummaryLoading && loadingUrl === article.url"
                        class="rotate"
                        height="14px"
                        src="@/assets/images/loading.svg"
                        alt=""
                      />
                      <img v-else src="@/assets/images/sparkles-thin.svg" height="14px" alt="" />
                      {{
                        articleSummaryLoading && loadingUrl === article.url
                          ? 'Summarizing'
                          : 'Summarize'
                      }}
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

                  <div class="regenerate-article">
                    <button
                      @click="toggleArticleRegenerate"
                      v-if="!showArticleRegenerate"
                      :disabled="articleSummaryLoading || loading || summaryLoading || savingSearch"
                      class="tertiary-button"
                    >
                      Regenerate
                    </button>

                    <div class="full-width" v-else>
                      <textarea
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                        autofocus
                        class="area-input-outline wider"
                        placeholder="Provide additional instructions..."
                        v-autoresize
                        v-model="articleInstructions"
                      />

                      <div class="row">
                        <button @click="toggleArticleRegenerate" class="secondary-button">
                          Cancel
                        </button>

                        <button
                          @click="getArticleSummary(article.url, articleInstructions)"
                          :disabled="
                            articleSummaryLoading || loading || summaryLoading || savingSearch
                          "
                          class="primary-button"
                        >
                          <img
                            v-if="articleSummaryLoading && loadingUrl === article.url"
                            class="rotate"
                            height="14px"
                            src="@/assets/images/loading.svg"
                            alt=""
                          />
                          {{
                            articleSummaryLoading && loadingUrl === article.url
                              ? 'Submitting'
                              : 'Submit'
                          }}
                        </button>
                      </div>
                    </div>
                  </div>
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
import { Comms } from '@/services/comms'

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
      showingPromptDropdown: false,
      sourceSummary: null,
      buttonText: 'Article Summary',
      AllUserTweets: {},
      mainView: 'news',
      savedSearch: null,
      tweets: [],
      tweetMedia: null,
      tweetUsers: null,
      articleInstructions: null,
      showUpdateBanner: false,
      showArticleRegenerate: false,
      showSaveName: false,
      isTyping: false,
      searchName: null,
      searchId: null,
      textIndex: 0,
      typedMessage: '',
      tweetError: '',
      savingSearch: false,
      starterNum: 0,
      newSearch: '',
      newTemplate: '',
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
      showingDropdown: false,
      copyTip: 'Copy',
      searchSuggestions: [
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
        'Articles written or about Ron Miller',
        'Rutgers University broad search',
        'Beyond meat broad search',
        'Beyond burger or sausage or meat',
        'Chick-fil-a competitors, list them out',
      ],
      promptSuggestions: [
        `Background on John Smith:\nTips for pitching John Smith:`,
        `Consumer Sentiment:\nMedia & Influencer Sentiment:`,
        `Executive Summary:\nFaculty, Research & Alumni:\nStudent life:`,
        `Executive Summary:\nImpact & Donor Insights:\nMember Impact:`,
        'What is the impact of this coverage on Tesla:',
        'Generate 5 questions and answers a journlist would ask based on this coverage',
        'Generate 5 questions and answers an analyst would ask based on this coverage of product X',
        'Suggest a strategy to combat the negative coverage',
        'Suggest a strategy to amplify the positive coverage,',
      ],
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
    soonButtonText() {
      this.buttonText = 'Coming Soon!'
    },
    defaultButtonText() {
      this.buttonText = 'Article Summary'
    },
    openTweet(username, id) {
      window.open(`https://twitter.com/${username}/status/${id}`, '_blank')
    },
    addSuggestion(ex) {
      this.newSearch = ex
      this.hideDropdown()
    },
    addPromptSuggestion(ex) {
      this.newTemplate = ex
      this.hidePromptDropdown()
    },
    async copyText() {
      try {
        const cleanedSummary = this.summary
          .split('<strong>')
          .filter((item) => item !== '<strong>')
          .join('')
          .split('</strong>')
          .filter((item) => item !== '</strong>')
          .join('')
        await navigator.clipboard.writeText(cleanedSummary)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    showDropdown() {
      this.showingDropdown = true
    },
    hideDropdown() {
      this.showingDropdown = false
    },
    showPromptDropdown() {
      this.showingPromptDropdown = true
    },
    hidePromptDropdown() {
      this.showingPromptDropdown = false
    },
    resetSearch() {
      this.clearNewSearch()
      this.$emit('change-search', null)
      this.summary = ''
    },
    switchMainView(view) {
      // if (view === 'news') {
      //   this.deselectOpp()
      // } else if (view !== 'meetings') {
      //   this.deselectMeeting()
      // }
      if (view !== this.mainView) {
        this.mainView = view
      }
    },
    formatNumber(num) {
      if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B'
      }
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
      }
      return num.toString()
    },
    toggleArticleRegenerate() {
      this.showArticleRegenerate = !this.showArticleRegenerate
    },
    toggleSaveName() {
      this.showSaveName = !this.showSaveName
    },
    setSearch(search) {
      this.summary = ''
      this.searchId = search.id
      this.searchName = search.name
      this.newSearch = search.input_text
      this.newTemplate = search.instructions
      this.mainView = search.type === 'SOCIAL_MEDIA' ? 'social' : 'news'
      this.generateNewSearch(search.search_boolean)
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
      this.textIndex = Math.floor(Math.random() * this.searchMessages.length)
      this.isTyping = true
      this.typedMessage = this.searchMessages[this.textIndex]
    },
    scrollToTop() {
      setTimeout(() => {
        this.$refs.loadedContent.scrollIntoView({ behavior: 'smooth' })
      }, 300)
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
    async generateNewSearch(boolean) {
      if (!this.newSearch || this.newSearch.length < 3) {
        return
      } else if (this.mainView === 'social') {
        this.getTweets()
      } else if (this.mainView === 'website') {
        this.getSourceSummary()
      } else {
        this.loading = true
        this.summaryLoading = true
        this.changeSearch({ search: this.newSearch, template: this.newTemplate })
        try {
          this.getClips(boolean).then((response) => {
            this.getSummary(this.filteredArticles, this.newTemplate).then((response) => {
              if (this.searchSaved) {
                this.updateSearch()
              }
            })
          })
        } catch (e) {
          console.log(e)
        }
      }
      this.closeRegenModal()
    },
    async getSourceSummary() {
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      this.summaryLoading = true
      try {
        await Comms.api
          .getArticleSummary({
            url: this.additionalSources,
            search: this.newSearch,
            instructions: this.newTemplate || null,
            length: 1000,
          })
          .then((response) => {
            console.log(response)
            this.summary = response.summary
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.summaryLoading = false
      }
    },
    async updateSearch() {
      try {
        await Comms.api
          .upateSearch({
            id: this.searchId,
            name: this.searchName,
            input_text: this.newSearch,
            search_boolean: this.booleanString,
            instructions: this.newTemplate,
          })
          .then((response) => {
            this.savedSearch = {
              name: this.searchName,
              input_text: this.newSearch,
              search_boolean: this.booleanString,
              instructions: this.newTemplate,
            }
          })
      } catch (e) {
        console.log('ERROR UPDATING SEARCH', e)
      }
    },
    clearNewSearch() {
      this.newSearch = ''
      this.newTemplate = ''
      this.searchName = ''
      this.additionalSources = ''
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
      this.showSaveName = false
      this.savingSearch = true
      try {
        const response = await Comms.api
          .createSearch({
            name: this.searchName || this.newSearch.slice(0, 60),
            input_text: this.newSearch,
            search_boolean: this.booleanString,
            instructions: this.newTemplate,
            type: this.mainView === 'news' ? 'NEWS' : 'SOCIAL_MEDIA',
          })
          .then((response) => {
            if (response.id) {
              this.searchId = response.id
              this.showUpdateBanner = true
              this.savedSearch = {
                name: response.name,
                input_text: this.newSearch,
                search_boolean: this.booleanString,
                instructions: this.newTemplate,
              }
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.savingSearch = false
        this.$store.dispatch('getSearches')
        setTimeout(() => {
          this.showUpdateBanner = false
        }, 2000)
      }
    },
    async getClips(boolean = null) {
      try {
        await Comms.api
          .getClips({
            search: this.newSearch,
            boolean: boolean,
            user_id: this.user.id,
          })
          .then((response) => {
            this.filteredArticles = response.articles
            this.booleanString = response.string
          })
      } catch (e) {
        this.clearNewSearch()
        this.filteredArticles = []
        console.log(e)
      } finally {
        this.loading = false
      }
    },
    async getTweets(boolean = null) {
      this.loading = true
      this.summaryLoading = true
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      try {
        await Comms.api
          .getTweets({
            search: this.newSearch,
            user_id: this.user.id,
          })
          .then((response) => {
            if (response.tweets) {
              this.tweets = response.tweets
              this.tweetMedia = response.includes.media
              this.booleanString = response.string
              this.getTweetSummary()
            }
          })
      } catch (e) {
        this.tweetError = e.data.error
        this.booleanString = e.data.string
        this.summaryLoading = false
        this.tweets = []
        this.tweetMedia = null
        this.clearNewSearch()
      } finally {
        this.loading = false
      }
    },
    prepareTweetSummary(tweets) {
      let tweetList = []
      for (let i = 0; i < tweets.length; i++) {
        tweetList.push(
          'Name :' +
            tweets[i].user.name +
            'tweet: ' +
            tweets[i].text +
            ' Follower count: ' +
            tweets[i].user.public_metrics.followers_count,
        )
      }
      return tweetList
    },
    getArticleDescriptions(articles) {
      return articles.map((a) => a.content)
    },
    async getTweetSummary(instructions = '') {
      let tweets = this.prepareTweetSummary(this.tweets)
      this.summaryLoading = true
      try {
        await Comms.api
          .getTweetSummary({
            tweets: tweets,
            search: this.newSearch,
            instructions: this.newTemplate,
          })
          .then((response) => {
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
    async getArticleSummary(url, instructions = null, length = 500) {
      this.articleSummaryLoading = true
      this.loadingUrl = url
      try {
        await Comms.api
          .getArticleSummary({
            url: url,
            search: this.newSearch,
            instructions: instructions,
            length: length,
          })
          .then((response) => {
            this.articleSummaries[url] = response.summary
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.showArticleRegenerate = false
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
    filteredSuggestions() {
      if (!this.newSearch) return this.searchSuggestions
      return this.searchSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.newSearch.toLowerCase()),
      )
    },
    filteredPromptSuggestions() {
      if (!this.newTemplate) return this.promptSuggestions
      return this.promptSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.newTemplate.toLowerCase()),
      )
    },
    searchSaved() {
      if (
        this.newSearch &&
        this.currentSearch &&
        this.currentSearch.input_text === this.newSearch
      ) {
        return true
      } else if (this.savedSearch && this.newSearch === this.savedSearch.input_text) {
        return true
      } else {
        return false
      }
    },
    fromNav() {
      return this.$store.state.fromNav
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
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
    clickOutsideMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
    clickOutsidePromptMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hidePromptDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
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

.dropdown {
  padding: 8px 0 8px 0;
  position: relative;
  height: fit-content;
  max-height: 232px;
  width: 100%;
  top: 8px;
  overflow-y: scroll;
  overflow-x: hidden;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  scroll-behavior: smooth;
}

.dropdown::-webkit-scrollbar {
  width: 6px;
  height: 0px;
  display: none;
}
.dropdown::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.dropdown:hover::-webkit-scrollbar {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 0;
  width: 100%;
  margin: 0;
  cursor: pointer;
  color: $dark-black-blue;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 400;
  font-size: 13px;
  z-index: 2300;

  p {
    margin: 0;
  }

  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-right: 8px;
  }

  &:hover {
    opacity: 0.7;
  }
}

.switcher {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
  background-color: $off-white;
  border: 1px solid $off-white;
  border-radius: 6px;
  padding: 4px 0;
  width: 300px;
  margin-top: 128px;
  margin-bottom: 16px;
}
.switch-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 6px;
  width: 100%;
  margin: 0 2px;
  cursor: pointer;
  color: $mid-gray;
  white-space: nowrap;
  font-weight: 400;
  font-size: 13px;
  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-right: 8px;
  }
}

.activeswitch {
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  img {
    filter: none;
  }
}

.relative {
  position: relative;
}
.absolute {
  position: absolute;
}
.regenerate-article {
  // background-color: red;
  // bottom: 0;
  // right: 16px;
}

.slide-fade-enter-active {
  transition: all 0.2s ease-in;
}

.slide-fade-leave-active {
  transition: all 0.1s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(100px);
}
.neg-margin {
  margin-left: -8px;
}

.templates {
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: 8px;
  left: 45%;
  font-size: 12px;
  background: $dark-green;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 2000;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.templates::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $dark-green;
  bottom: -3px;
  left: 45%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
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
  display: flex;
  align-items: center;
  flex-direction: row;
  overflow: hidden;
  white-space: nowrap;
  width: 0;
  animation: typing 2s steps(30, end) forwards, blinking 1s infinite;
  // border-right: 1px solid;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;
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

.invert {
  filter: invert(70%);
}

// .invert-dark-blue {
//   filter: invert(22%) sepia(51%) saturate(390%) hue-rotate(161deg) brightness(92%) contrast(87%);
// }

// .img-border {
//   border: 1px solid #416177;
//   border-radius: 100%;
//   padding: 0px 4px;
//   margin-left: 8px;
//   cursor: pointer;
//   img {
//     margin: 0 !important;
//     filter: invert(33%) sepia(27%) saturate(676%) hue-rotate(161deg) brightness(95%) contrast(84%);
//   }
// }

// .img-border:hover {
//   background: #416177;

//   img {
//     filter: invert(100%);
//   }
// }

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
.pad-btm {
  padding-bottom: 16px;
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

::placeholder {
  color: $mid-gray;
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

.no-hover-effect:hover {
  scale: 1;
  box-shadow: none;
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-type {
  cursor: pointer;
  p {
    padding: 0;
    margin: 0;
    font-weight: 400;
    font-size: 13px;
    color: $dark-black-blue;
  }

  img {
    filter: invert(40%);
    margin-left: 8px;
  }
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;
}

.column {
  flex-direction: column;
  height: 100%;
}

.fullHeight {
  // margin-top: -10vh;
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
  position: relative;
}
.s-padding {
  padding: 0 0.25rem !important;
}
.area-input-outline {
  width: 300px;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  padding: 5px 8px;
  border-radius: 4px;
  line-height: 1.75;
  border: 1px solid rgba(0, 0, 0, 0.1);
  outline: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $base-font-family;
  font-weight: 400;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  margin-right: 1rem;
  resize: none;
}

.full-width {
  width: 100%;
}

.wider {
  width: 100%;
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

.twitter-blue {
  filter: invert(49%) sepia(87%) saturate(1104%) hue-rotate(175deg) brightness(95%) contrast(101%);
  margin-left: 8px;
}
.area-input::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}
.input-row {
  display: flex;
  align-items: center;
  flex-direction: row;
}
.input-row-start {
  display: flex;
  align-items: flex-start;
  flex-direction: row;

  img,
  small {
    margin-top: 4px;
  }
}
.main-text {
  display: flex;
  flex-direction: row;
  align-items: center;
  white-space: nowrap;
  // padding-right: 0;
  margin: 0;
  svg {
    margin-right: 4px;
  }
}

.main-slot {
  width: 28px;
  height: 28px;
  border-radius: 100%;
  background-color: $dark-black-blue;
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    filter: invert(99%);
    margin: 0;
    padding: 0;
  }
}

.slot-container {
  margin-top: 32px;
}

.empty-slot {
  border-radius: 100%;
  height: 10px;
  width: 10px;
  margin-bottom: 16px;
  background-color: rgba(108, 106, 106, 0.1);
}

.floating-action-bar {
  background-color: $white-blue;
  position: fixed;
  z-index: 3000;
  right: 24px;
  top: 40vh;
  height: 150px;
  border-radius: 32px;
  border: 1px solid $white-blue;
  width: 34px;
  display: flex;
  padding-top: 4px;
  flex-direction: column;
  align-items: center;
}

.main-content {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  position: relative;
  border-radius: 8px;
  padding: 58px 36px 0 36px;
  height: fit-content;
  width: 100vw;
  color: $dark-blue;
  overflow-y: scroll;
}

.suggestions {
  position: absolute;
  bottom: 1rem;
  z-index: 2100;
  right: 1.5rem;
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

.img-highlight {
  filter: invert(40%);

  &:hover {
    filter: none;
  }
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

.wbbackground {
  background-color: $white-blue;
}

.loader-bg {
  width: 50%;
  align-items: center;
  justify-content: center;
  background-color: $white-blue;
}

.no-content {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;

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
  position: relative;
  display: flex;
  justify-content: flex-start;
  width: 100%;
  margin-bottom: 0;
  background-color: $off-white;
  padding-top: 0;
  padding-bottom: 40px;
}
.clips-container {
  padding-top: 16px;
  display: flex;
  justify-content: flex-start;
  width: 100%;
  background-color: white;
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

.news-container-med {
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
}

.no-results {
  display: flex;
  align-items: center;
  justify-content: center;

  font-weight: 400;
  font-size: 13px;
  color: #6b6b6b;
}

.title-container {
  position: relative;
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}

.back {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0.75rem;
  left: -56px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 100%;
  padding: 3px 2px;
  cursor: pointer;

  img {
    filter: invert(40%);
  }
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

.news-card-medium {
  position: relative;
  min-height: 200px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 0 0 1rem 0;
  margin-bottom: 1rem;

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    height: 60px;
    overflow: none;
    text-overflow: ellipsis;
    margin-bottom: 8px;
  }
}

.card-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.card-row-med {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  img {
    height: 20px;
    margin-right: 0.5rem;
  }
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

.cover-photo-no-l-margin {
  height: 112px;
  width: 116px;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: text;
  border-radius: 4px;
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

.article-preview-medium {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
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
  width: 500px;
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
  padding-top: 16px;
  padding-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.blue-border-button {
  @include dark-blue-border-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  width: 8rem;
  margin-bottom: 1rem;
}
.cancel-button {
  @include gray-text-button();
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}
.save-button {
  @include dark-blue-button();
  &:hover {
    scale: 1;
    opacity: 0.9;
    box-shadow: none;
  }
  margin-left: 0.5rem;
}
.pointer {
  cursor: pointer;
}
.regen-modal {
  margin-top: 84px;
}
.regen-container {
  width: 500px;
  max-height: 500px;
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

.gray-text {
  color: $mid-gray;
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
.meta-shortest {
  width: 60%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-small {
  width: 40%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}

.bold-text {
  font-weight: bold;
  color: $base-gray;
  font-size: 12px;

  span {
    color: #6b6b6b;
  }
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
  // background-color: ;
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

.red-text {
  color: $coral;
  font-weight: 400;
  font-size: 12px;
}
</style>