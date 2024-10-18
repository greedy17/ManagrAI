<template>
  <div class="reports">
    <div v-if="creating">
      <div class="chat-window">
        <div class="chat-window__header">
          <p>Coverage Report</p>
        </div>

        <div ref="chatWindow" class="chat-window__body">
          <div class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>Help me create a coverage report</p>
            </div>
          </div>

          <div>
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="nameText"></p>
              </div>
            </div>
          </div>

          <div
            @mouseenter="hoveringName = true"
            @mouseleave="hoveringName = false"
            v-if="reportName"
            class="space-between"
          >
            <div></div>

            <div style="position: relative" class="chat-window__chat-bubble row">
              <div
                @click="toggleEditName"
                v-if="!editingName && hoveringName"
                style="cursor: pointer"
                class="abs-img-left"
              >
                <img src="@/assets/images/pencil.svg" height="14px" alt="" />
              </div>

              <div
                @click="updateName"
                v-else-if="hoveringName"
                style="cursor: pointer"
                class="abs-img-left"
              >
                <img src="@/assets/images/close.svg" height="18px" alt="" />
              </div>

              <div v-if="!editingName" class="row">
                <img src="@/assets/images/profile.svg" height="12px" alt="" />
                <p>{{ reportName }}</p>
              </div>

              <div v-else style="opacity: 1; margin: 0; cursor: text" class="input-container-small">
                <input
                  style="border: none; outline: none; padding: 10px 8px 10px 0px; width: 100%"
                  type="text"
                  @keyup.enter="updateName"
                  v-model="reportName"
                  placeholder="Brand name..."
                />

                <div
                  class="img-container-stay-small-txt"
                  v-if="reportName"
                  @click="updateName"
                  style="margin-right: 12px; padding: 1px 6px 2px 6px"
                >
                  Save
                  <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
                </div>

                <img
                  v-else
                  style="filter: invert(40%); margin-right: 20px"
                  src="@/assets/images/edit.svg"
                  height="14px"
                  alt=""
                />
              </div>
            </div>
          </div>

          <div v-if="reportName">
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="brandText"></p>
              </div>
            </div>
          </div>

          <div
            @mouseenter="hovering = true"
            @mouseleave="hovering = false"
            v-if="brand"
            class="space-between"
          >
            <div></div>

            <div style="position: relative" class="chat-window__chat-bubble">
              <div
                @click="toggleEditBrand"
                v-if="!editingBrand && hovering"
                style="cursor: pointer"
                class="abs-img-left"
              >
                <img src="@/assets/images/pencil.svg" height="14px" alt="" />
              </div>

              <div
                @click="updateBrand"
                v-else-if="hovering"
                style="cursor: pointer"
                class="abs-img-left"
              >
                <img src="@/assets/images/close.svg" height="18px" alt="" />
              </div>

              <div class="row" v-if="!editingBrand">
                <img src="@/assets/images/profile.svg" height="12px" alt="" />
                <p>{{ brand }}</p>
              </div>

              <div v-else style="opacity: 1; margin: 0; cursor: text" class="input-container-small">
                <input
                  style="border: none; outline: none; padding: 10px 8px 10px 0px; width: 100%"
                  type="text"
                  @keyup.enter="updateBrand"
                  v-model="brand"
                  placeholder="Brand name..."
                />

                <div
                  class="img-container-stay-small-txt"
                  v-if="brand"
                  @click="updateBrand"
                  style="margin-right: 12px; padding: 1px 6px 2px 6px"
                >
                  Save
                  <img src="@/assets/images/arrow-right.svg" class="pointer" height="10px" alt="" />
                </div>

                <img
                  v-else
                  style="filter: invert(40%); margin-right: 20px"
                  src="@/assets/images/edit.svg"
                  height="14px"
                  alt=""
                />
              </div>
            </div>
          </div>

          <div v-if="brand">
            <div style="width: fit-content" class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="uploadText"></p>
              </div>

              <div style="margin: 0 0 8px 14px" class="row">
                <div class="file-input-wrapper">
                  <label class="file-input-label">
                    <input type="file" @change="uploadImage" class="file-input" />
                    <span style="margin-right: 4px" class="secondary-button">
                      <img
                        v-if="loading"
                        style="margin-right: 4px"
                        class="invert rotation"
                        src="@/assets/images/loading.svg"
                        height="14px"
                        alt=""
                      />
                      Upload Banner
                    </span>
                  </label>
                  <p style="margin-left: 8px" class="file-name">
                    {{ fileName ? fileName : 'No file selected' }}
                  </p>

                  <img
                    v-if="fileName"
                    style="margin-left: 8px"
                    :src="uploadedImageUrl"
                    height="40px"
                    alt=""
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-if="fileName" class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>{{ fileName }} uploaded</p>
            </div>
          </div>

          <div v-if="fileName">
            <div style="width: 80%" class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="fileText"></p>
              </div>

              <div style="margin: 0 0 8px 14px">
                <p class="thin-font">
                  Paste up to 200 URLs. Each on a new line or separated by commas.
                </p>
                <textarea
                  style="
                    width: 100%;
                    border: 1px solid rgba(0, 0, 0, 0.1) !important;
                    padding: 12px;
                  "
                  :rows="5"
                  id="search-input"
                  class="area-input"
                  autocomplete="off"
                  :placeholder="urlPlaceholder"
                  v-model="reportUrls"
                  v-autoresize
                  :disabled="urlsSet"
                  @input="handleInput"
                />
                <div style="margin-top: 12px" class="flex-end">
                  <button
                    @click="setUrls"
                    :disabled="!reportUrls || urlsSet"
                    class="primary-button"
                  >
                    Continue
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="urlsSet" class="space-between">
            <div></div>
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/profile.svg" height="12px" alt="" />
              <p>{{ urlCount }} URLs uploaded</p>
            </div>
          </div>

          <div v-if="urlsSet">
            <div class="big-chat-bubble">
              <div class="row">
                <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
                <p class="regular-font" v-typed="lastInstructions"></p>
              </div>

              <div style="margin: 0 0 8px 8px">
                <button :disabled="loading" @click="getReportClips" class="primary-button">
                  Run report
                </button>
              </div>
            </div>
          </div>

          <div v-if="loading" class="space-between">
            <div class="chat-window__chat-bubble row">
              <img src="@/assets/images/iconlogo.png" height="24px" alt="" />
              <p style="margin-right: 6px">{{ loadingText }}</p>
              <img class="rotation" src="@/assets/images/loading.svg" height="14px" alt="" />
            </div>
            <div></div>
          </div>
        </div>

        <div class="chat-window__footer">
          <div class="large-input-container">
            <div style="border-radius: 28px" class="input-container-gray">
              <section>
                <textarea
                  ref="textarea"
                  style="width: 100%"
                  :rows="1"
                  id="search-input"
                  class="area-input"
                  autocomplete="off"
                  placeholder="Message ManagrAI..."
                  v-model="searchText"
                  v-autoresize
                  :disabled="loading || (!!brand && !!reportName)"
                  @keyup.enter="generateReportSearch($event)"
                />

                <div
                  v-if="searchText"
                  @click="generateReportSearch($event)"
                  class="left-margin pointer lite-bg img-container-stay-alt"
                  style="margin-right: 16px"
                >
                  <img
                    style="margin: 0"
                    src="@/assets/images/paper-plane-full.svg"
                    height="12px"
                    alt=""
                  />
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="fadein" v-else>
      <div class="chat-window">
        <div class="chat-window__header">
          <p class="thin-font">
            <span class="bold-font">{{ brand }}</span> Coverage Report
          </p>
          <div :class="{ opaque: editSummary }" class="row">
            <button @click="clearData" class="secondary-button">Back</button>
            <button
              v-if="!reportLink"
              :disabled="reportLoading || loading"
              :loading="reportLoading"
              @click="createReport"
              class="primary-button"
            >
              Save
              <img
                v-if="reportLoading"
                style="margin-left: 6px"
                class="rotation invert"
                src="@/assets/images/loading.svg"
                height="14px"
                alt=""
              />
            </button>

            <button :disabled="loading" v-else @click="viewReport" class="primary-button">
              View Report
            </button>

            <!-- <img src="@/assets/images/disk.svg" height="14px" alt="" /> -->
          </div>
        </div>

        <div class="chat-window__body">
          <div v-if="view === 'home'">
            <div :class="{ opaque: loading }" style="padding-top: 20px" class="container fadein">
              <div>
                <img :src="uploadedImageUrl" class="photo-header" />
              </div>
              <div style="margin-top: 12px" v-if="editSummary" class="space-between fadein">
                <div></div>
                <button @click="closeSummaryEdit" class="primary-button turq-bg">
                  Update Report
                </button>
              </div>
              <pre
                ref="editablePre"
                :class="{ text: editSummary }"
                v-html="summary"
                @input="updateSummary"
                :contenteditable="editSummary"
                class="pre-text"
              ></pre>
            </div>
          </div>

          <div class="fadein" v-else-if="view === 'charts'">
            <div class="container fadein">
              <div class="space-between bottom-margin">
                <div class="col">
                  <p class="bold-font medium-txt">Total coverage</p>
                  <small>Number of news clips in this report</small>
                </div>

                <p class="bold-font">{{ clips.length }}</p>
              </div>

              <div class="space-between bottom-margin">
                <div class="col">
                  <p class="bold-font medium-txt">Unique visitors</p>
                  <small>The potential audience reached by your media coverage</small>
                </div>

                <div class="row">
                  <img
                    style="margin-right: 8px"
                    src="@/assets/images/users.svg"
                    height="16px"
                    alt=""
                  />
                  <p class="bold-font">{{ formatNumber(totalVisits) }}</p>
                </div>
              </div>

              <div class="space-between">
                <div class="col">
                  <p class="bold-font medium-txt">Total shares</p>
                  <small>Number of times content was shared on social media</small>
                </div>

                <section class="row img-mar">
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/facebook.png" height="20px" alt="" />
                    <p class="bold-font">{{ socialTotals.totalFacebookLikes }}</p>
                  </div>
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/twitter-x.svg" height="16px" alt="" />
                    <p class="bold-font">{{ socialTotals.totalTwitterLikes }}</p>
                  </div>
                  <div style="margin-right: 12px" class="row">
                    <img src="@/assets/images/reddit.svg" height="20px" alt="" />
                    <p class="bold-font">{{ socialTotals.totalRedditLikes }}</p>
                  </div>
                  <div class="row">
                    <img src="@/assets/images/pinterest.png" height="20px" alt="" />
                    <p class="bold-font">{{ socialTotals.totalPinterestLikes }}</p>
                  </div>
                </section>
              </div>
            </div>

            <div class="container">
              <div class="col bottom-margin">
                <p class="bold-font medium-txt">Media exposure over time</p>
                <small>Number of media clips along with the potential reach</small>
              </div>
              <ReportLineChart
                :volume="clipChartData.clipCountList"
                :reach="clipChartData.usersList"
                :dates="clipChartData.dateList"
              />
            </div>
          </div>
          <div ref="topDivider" class="fadein" v-else-if="view === 'starred'">
            <div class="fadein" v-if="!starredArticles.length">
              <p class="row">
                Your starred articles<span style="margin: 0 6px"
                  ><img src="@/assets/images/newspaper.svg" height="14px" alt=""
                /></span>
                will appear here
              </p>
            </div>

            <div v-else>
              <div v-for="(article, i) in starredArticles" :key="i" class="container fadein">
                <div style="position: relative" class="container__top">
                  <div class="abs-top-right">
                    <img
                      @click="starArticle(article)"
                      class="blue-filter fadein"
                      style="cursor: pointer"
                      src="@/assets/images/fullstar.svg"
                      height="16px"
                      alt=""
                    />
                  </div>
                  <div style="margin-bottom: 12px">
                    <img
                      @error="onImageError($event)"
                      :src="article.image"
                      class="photo-header-small"
                    />
                  </div>

                  <div class="space-between no-letter-margin">
                    <div class="col">
                      <p class="bold-font">
                        {{ article.traffic ? removeDomain(article.traffic.target) : 'unknown' }}
                      </p>
                      <div style="margin-top: 8px" class="row">
                        <img
                          style="margin-right: 4px"
                          src="@/assets/images/profile.svg"
                          height="12px"
                          alt=""
                        />
                        <p>{{ article.author[0] ? article.author[0] : 'Unkown' }}</p>
                      </div>
                    </div>
                    <small>{{ getTimeDifferenceInMinutes(article.date) }}</small>
                  </div>

                  <div>
                    <!-- <h3 style="margin: 20px 0" class="bold-font elipsis-text">
                      {{ article.description }}
                    </h3> -->

                    <div class="elipsis-text" style="margin: 20px 0">
                      <a :href="article.url" target="_blank" class="bold-txt">
                        {{ article.description }}</a
                      >
                    </div>
                  </div>

                  <div class="space-between bottom-margin-m">
                    <div class="row img-mar">
                      <img src="@/assets/images/users.svg" height="14px" alt="" />
                      <p class="bold-font">
                        {{ article.traffic ? formatNumber(article.traffic.users) : 0 }}
                      </p>
                    </div>

                    <section class="row img-mar">
                      <div style="margin-right: 12px" class="row">
                        <img src="@/assets/images/facebook.png" height="14px" alt="" />
                        <p class="bold-font">
                          {{
                            formatNumber(
                              socialData[article.url] && socialData[article.url][0]
                                ? socialData[article.url][0]['total_facebook_shares']
                                  ? socialData[article.url][0]['total_facebook_shares']
                                  : 0
                                : 0,
                            )
                          }}
                        </p>
                      </div>

                      <div style="margin-right: 12px" class="row">
                        <img
                          style="margin-right: 4px"
                          src="@/assets/images/twitter-x.svg"
                          height="14px"
                          alt=""
                        />
                        <p class="bold-font">
                          {{
                            formatNumber(
                              socialData[article.url] && socialData[article.url][0]
                                ? socialData[article.url][0]['twitter_shares']
                                  ? socialData[article.url][0]['twitter_shares']
                                  : 0
                                : 0,
                            )
                          }}
                        </p>
                      </div>

                      <div style="margin-right: 12px" class="row">
                        <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                        <p class="bold-font">
                          {{
                            formatNumber(
                              socialData[article.url] && socialData[article.url][0]
                                ? socialData[article.url][0]['total_reddit_engagements']
                                  ? socialData[article.url][0]['total_reddit_engagements']
                                  : 0
                                : 0,
                            )
                          }}
                        </p>
                      </div>

                      <div class="row">
                        <img
                          style="margin-right: 4px"
                          src="@/assets/images/pinterest.png"
                          height="14px"
                          alt=""
                        />
                        <p class="bold-font">
                          {{
                            formatNumber(
                              socialData[article.url] && socialData[article.url][0]
                                ? socialData[article.url][0]['pinterest_shares']
                                  ? socialData[article.url][0]['pinterest_shares']
                                  : 0
                                : 0,
                            )
                          }}
                        </p>
                      </div>

                      <!-- <div class="row">
                      <img src="@/assets/images/twitter-x.svg" height="12px" alt="" />
                      <p class="bold-font">1,000</p>
                    </div>
                    <div class="row">
                      <img src="@/assets/images/reddit.svg" height="14px" alt="" />
                      <p class="bold-font">10,000</p>
                    </div> -->
                    </section>
                  </div>
                </div>

                <div v-if="article.summary" class="report-body">
                  <div style="margin-top: 12px">
                    <pre v-html="article.summary" class="pre-text"></pre>
                  </div>
                </div>

                <div v-else class="report-body">
                  <div class="space-between" style="margin-top: 12px">
                    <div></div>
                    <button
                      :disabled="summaryLoading || loading"
                      @click="getArticleSummary(article.url)"
                      class="primary-button"
                    >
                      Summarize
                      <img
                        v-if="summaryLoading && loadingUrl === article.url"
                        style="margin-left: 6px"
                        class="rotation invert"
                        src="@/assets/images/loading.svg"
                        height="14px"
                        alt=""
                      />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="fadein" v-else-if="view === 'articles'">
            <div class="container fadein">
              <div v-for="(article, i) in clips" :key="i" class="article">
                <div class="space-between">
                  <p class="bold-font">
                    {{ article.traffic ? removeDomain(article.traffic.target) : 'unknown' }}
                  </p>
                  <img
                    v-if="!starredArticles.includes(article)"
                    @click="starArticle(article)"
                    style="cursor: pointer"
                    class="fadein"
                    src="@/assets/images/star.svg"
                    height="16px"
                    alt=""
                  />
                  <img
                    v-else
                    @click="starArticle(article)"
                    class="blue-filter fadein"
                    style="cursor: pointer"
                    src="@/assets/images/fullstar.svg"
                    height="16px"
                    alt=""
                  />
                </div>

                <div class="space-between-bottom">
                  <div class="article-body">
                    <!-- <h3 class="bold-font">
                      {{ article.title }}
                    </h3> -->

                    <div style="margin: 20px 0">
                      <a :href="article.url" target="_blank" class="bold-txt elipsis-text">
                        {{ article.title }}</a
                      >
                    </div>

                    <p class="report-body">
                      {{ article.description }}
                    </p>
                  </div>

                  <img
                    @error="onImageError($event)"
                    :src="article.image"
                    class="photo-header-alt"
                  />
                </div>

                <div style="margin-top: 12px" class="space-between bottom-border">
                  <div class="row report-body">
                    <div class="pill">
                      <img src="@/assets/images/profile.svg" height="12px" alt="" />
                      <p style="margin-right: 6px">
                        {{ article.author && article.author[0] ? article.author[0] : 'Unkown' }}
                      </p>
                    </div>

                    <small>{{ getTimeDifferenceInMinutes(article.date) }}</small>
                  </div>

                  <div class="row small-text">
                    <div style="margin-right: 16px" class="row img-mar">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/users.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{ article.traffic ? formatNumber(article.traffic.users) : 0 }}
                      </p>
                    </div>

                    <div style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/facebook.png"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{
                          formatNumber(
                            socialData[article.url] && socialData[article.url][0]
                              ? socialData[article.url][0]['total_facebook_shares']
                                ? socialData[article.url][0]['total_facebook_shares']
                                : 0
                              : 0,
                          )
                        }}
                      </p>
                    </div>
                    <div style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/twitter-x.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{
                          formatNumber(
                            socialData[article.url] && socialData[article.url][0]
                              ? socialData[article.url][0]['twitter_shares']
                                ? socialData[article.url][0]['twitter_shares']
                                : 0
                              : 0,
                          )
                        }}
                      </p>
                    </div>
                    <div style="margin-right: 16px" class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/reddit.svg"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{
                          formatNumber(
                            socialData[article.url] && socialData[article.url][0]
                              ? socialData[article.url][0]['total_reddit_engagements']
                                ? socialData[article.url][0]['total_reddit_engagements']
                                : 0
                              : 0,
                          )
                        }}
                      </p>
                    </div>

                    <div class="row">
                      <img
                        style="margin-right: 4px"
                        src="@/assets/images/pinterest.png"
                        height="14px"
                        alt=""
                      />
                      <p class="bold-font">
                        {{
                          formatNumber(
                            socialData[article.url] && socialData[article.url][0]
                              ? socialData[article.url][0]['pinterest_shares']
                                ? socialData[article.url][0]['pinterest_shares']
                                : 0
                              : 0,
                          )
                        }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <nav v-if="!creating" class="left-nav">
      <ul class="nav-links">
        <li @click="changeView('home')" class="nav-item s-wrapper">
          <div :class="{ active: view === 'home' }">
            <img src="@/assets/images/home.svg" height="16px" alt="" />
          </div>

          <section class="s-tooltip-right">Home</section>
        </li>

        <li @click="changeView('charts')" class="nav-item s-wrapper">
          <div :class="{ active: view === 'charts' }">
            <img src="@/assets/images/stats.svg" height="16px" alt="" />
          </div>
          <section class="s-tooltip-right">Traffic</section>
        </li>

        <li @click="changeView('starred')" class="nav-item s-wrapper">
          <div :class="{ active: view === 'starred' }">
            <img src="@/assets/images/star.svg" height="16px" alt="" />
          </div>
          <section class="s-tooltip-right">Starred</section>
        </li>

        <li @click="changeView('articles')" class="nav-item s-wrapper">
          <div :class="{ active: view === 'articles' }">
            <img src="@/assets/images/newspaper.svg" height="16px" alt="" />
          </div>
          <section class="s-tooltip-right">Articles</section>
        </li>
      </ul>
    </nav>

    <div v-if="!creating && view == 'home'">
      <div @click.stop="openPanel" :class="{ expanded: panelOpen }" class="floating-panel">
        <div
          v-outside-click="closePanel"
          class="fadein panel-options"
          v-show="panelOpen && !loading"
        >
          <div v-if="showingReportEdit" class="abs-top">
            <div class="space-between">
              <p class="bold-txt">Regenerate</p>
              <img
                style="cursor: pointer"
                @click="showingReportEdit = !showingReportEdit"
                src="@/assets/images/close.svg"
                height="20px"
                alt=""
              />
            </div>

            <div>
              <textarea
                style="
                  width: 100%;
                  border: 1px solid rgba(0, 0, 0, 0.1) !important;
                  padding: 12px;
                  min-height: 100px;
                "
                :rows="5"
                id="search-input"
                class="area-input"
                autocomplete="off"
                placeholder="provide additional instructions for a new summary..."
                v-model="reportInstructions"
                v-autoresize
                :disabled="loading"
              />
              <div class="space-between">
                <div></div>
                <button @click="rewriteContent(reportInstructions)" class="primary-button">
                  Regenerate

                  <img
                    v-if="loading"
                    style="margin-left: 6px"
                    class="rotation invert"
                    src="@/assets/images/loading.svg"
                    height="14px"
                    alt=""
                  />
                </button>
              </div>
            </div>
          </div>

          <div @click="editSummary = !editSummary" class="s-wrapper">
            <img src="@/assets/images/pencil.svg" height="18px" alt="" />
            <section class="s-tooltip-left">Edit</section>
          </div>
          <div @click="showingReportEdit = !showingReportEdit" class="s-wrapper">
            <img src="@/assets/images/refresh-pr.svg" height="18px" alt="" />
            <section class="s-tooltip-left">Regenerate</section>
          </div>
          <div class="s-wrapper" @click="rewriteContent(shortText)">
            <img src="@/assets/images/sortup.svg" height="18px" alt="" />
            <section class="s-tooltip-left">Make shorter</section>
          </div>
          <div @click="rewriteContent(longText)" class="s-wrapper">
            <img src="@/assets/images/sortdwn.svg" height="18px" alt="" />
            <section class="s-tooltip-left">Make longer</section>
          </div>
        </div>
        <img
          v-if="!loading"
          :class="{ opaque: panelOpen }"
          src="@/assets/images/wand.svg"
          height="20px"
          alt=""
        />
        <img v-else class="rotation" src="@/assets/images/loading.svg" height="20px" alt="" />
      </div>
    </div>
  </div>
</template>

<script>
import ReportLineChart from '@/components/ReportLineChart.vue'
import { Comms } from '@/services/comms'
import User from '@/services/users'

export default {
  name: 'Reports',
  components: {
    ReportLineChart,
  },
  data() {
    return {
      editSummary: false,
      shortText: 'The report is too long. Make it shorter',
      longText: "The report isn't long enough. Make it longer",
      showingReportEdit: false,
      preppedClips: [],
      reportInstructions: '',
      panelOpen: false,
      hoveringName: false,
      hovering: false,
      editingBrand: false,
      editingName: false,
      reportLink: null,
      mainImage: null,
      reportLoading: false,
      summaryLoading: false,
      loadingUrl: null,
      clipChartData: null,
      socialTotals: null,
      socialData: null,
      totalVisits: 0,
      starredArticles: [],
      logoPlaceholder: require('@/assets/images/iconlogo.png'),
      traffic: null,
      urlCount: 0,
      urls: [],
      clips: [],
      loadingText: 'Analyzing articles...',
      summary: '',
      view: 'home',
      creating: true,
      reportName: '',
      brandText: 'Next, tell us which brand this report is for (e.g. Nike, Tesla, FSU)',
      nameText: 'Using the message bar below, provide a name for your report',
      loading: false,
      brand: '',
      searchText: '',
      uploadText: 'Upload banner image using JPEG, PNG, or SVG',
      fileName: '',
      allowedFormats: [
        'image/jpeg',
        'image/png',
        'image/svg+xml',
        'image/webp',
        'image/gif',
        'image/tiff',
        'image/bmp',
        'application/pdf',
      ],
      maxSize: 2 * 1024 * 1024,
      fileText: `Next, add news coverage links by pasting the URL's below.`,
      reportUrls: '',
      urlsSet: false,
      urlPlaceholder: `
www.techcrunch.com/article-1 
www.bloomberg.com/article-2
www.forbes.com/article-3
     `,
      lastInstructions: 'All set! We are now ready to run the report!',
      uploadedImageUrl: '',
    }
  },
  watch: {
    editSummary(newVal) {
      console.log(newVal)
      if (newVal) {
        this.$nextTick(() => {
          this.$refs.editablePre.focus()
          this.panelOpen = false
        })
      }
    },
  },
  computed: {
    reports() {
      return this.$store.state.allReports
    },
  },
  methods: {
    closeSummaryEdit() {
      this.editSummary = false
    },
    updateSummary() {
      let selection = window.getSelection()
      let range = selection.getRangeAt(0)

      // Save the caret position as a character offset
      let preText = this.$refs.editablePre.innerText
      let caretOffset = this.getCaretCharacterOffsetWithin(this.$refs.editablePre)

      // Update summary with innerHTML to preserve formatting
      this.summary = this.$refs.editablePre.innerHTML

      this.$nextTick(() => {
        // Restore caret position after updating
        this.setCaretPosition(this.$refs.editablePre, caretOffset)
      })
    },

    // Helper function to get caret character offset within a contenteditable element
    getCaretCharacterOffsetWithin(element) {
      let caretOffset = 0
      let selection = window.getSelection()
      if (selection.rangeCount > 0) {
        let range = selection.getRangeAt(0)
        let preCaretRange = range.cloneRange()
        preCaretRange.selectNodeContents(element)
        preCaretRange.setEnd(range.endContainer, range.endOffset)
        caretOffset = preCaretRange.toString().length
      }
      return caretOffset
    },

    // Helper function to set the caret position at a specific character offset
    setCaretPosition(element, offset) {
      let selection = window.getSelection()
      let range = document.createRange()
      let currentNode = element
      let currentOffset = 0

      // Traverse the child nodes to find the correct text node for the caret position
      function traverseNodes(node) {
        if (node.nodeType === 3) {
          // Text node
          if (currentOffset + node.length >= offset) {
            range.setStart(node, offset - currentOffset)
            return true
          } else {
            currentOffset += node.length
          }
        } else {
          for (let i = 0; i < node.childNodes.length; i++) {
            if (traverseNodes(node.childNodes[i])) return true
          }
        }
        return false
      }

      traverseNodes(element)

      // Set the caret to the calculated position
      selection.removeAllRanges()
      selection.addRange(range)
    },
    openPanel() {
      if (!this.loading) {
        this.panelOpen = true
      }
    },
    closePanel() {
      this.panelOpen = false
      this.showingReportEdit = false
    },
    refreshUser() {
      User.api
        .getUser(this.user.id)
        .then((user) => {
          this.$store.dispatch('updateUser', user)
          return user
        })
        .catch(() => {
          return null
        })
    },
    updateBrand() {
      this.editingBrand = false
    },
    toggleEditBrand() {
      this.editingBrand = true
    },
    updateName() {
      this.editingName = false
    },
    toggleEditName() {
      this.editingName = true
    },
    removeDomain(url) {
      const domainRegex = /\.(com|net|org|gov|edu|co|io|biz|info|us)$/i

      return url.replace(domainRegex, '')
    },
    clearData() {
      this.$router.go(0)
    },
    viewReport() {
      window.open(this.reportLink, '_blank')
    },
    async createReport() {
      this.reportLoading = true
      let formData = new FormData()
      formData.append('title', this.reportName)
      formData.append('main_image', this.mainImage)
      formData.append('user', this.$store.state.user.id)
      formData.append(
        'meta_data',
        JSON.stringify({
          clips: this.clips,
          summary: this.summary,
          chartData: this.clipChartData,
          starredArticles: this.starredArticles,
          socialData: this.socialData,
          socialTotals: this.socialTotals,
          totalVisits: this.totalVisits,
          urlCount: this.urlCount,
          brand: this.brand,
        }),
      )

      try {
        await User.api.createReport(formData)
        this.$nextTick(() => {
          this.getReports()
          this.refreshUser()
        })
        this.$toast('Report Saved!', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.reportLoading = false
      }
    },
    // async getReports() {
    //   try {
    //     await User.api.getReports({ user: this.$store.state.user.id }).then((response) => {
    //       this.reportLink = response.results[0]['share_url']
    //     })
    //   } catch (e) {
    //     console.log(e)
    //   } finally {
    //   }
    // },
    getReports() {
      this.$store.dispatch('getReports')
      this.reportLink = this.reports[0].share_url
    },
    scrollToTopDivider() {
      setTimeout(() => {
        this.$refs.topDivider.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    },
    async getArticleSummary(url, instructions = null, length = 1000) {
      let selectedClip = []

      selectedClip = this.starredArticles.filter((art) => art.url === url)[0]

      this.summaryLoading = true
      this.loadingUrl = url

      try {
        const response = await Comms.api.getArticleSummary({
          url: url,
          search: this.brand,
          instructions: instructions,
          length: length,
        })

        selectedClip['summary'] = response.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')

        if (!this.starredArticles.length) {
          this.starredArticles = this.starredArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.starredArticles.unshift(selectedClip)
        } else {
          this.starredArticles = this.starredArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.starredArticles.unshift(selectedClip)
        }
        this.scrollToTopDivider()
      } catch (e) {
        console.log(e)
        this.$toast('Request blocked by article source', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.summaryLoading = false
        this.loadingUrl = null
      }
    },
    starArticle(art) {
      const index = this.starredArticles.findIndex((a) => a.url === art.url)

      if (index === -1) {
        this.starredArticles = [...this.starredArticles, art]
      } else {
        this.starredArticles = this.starredArticles.filter((a) => a.url !== art.url)
      }
    },
    getTimeDifferenceInMinutes(dateString) {
      if (dateString) {
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
          let month
          let day
          let year
          if (Number(givenDate.getMonth() + 1)) {
            month = givenDate.getMonth() + 1
          } else {
            month = '--'
          }
          if (Number(givenDate.getDate())) {
            day = givenDate.getDate()
          } else {
            day = '--'
          }
          if (Number(givenDate.getFullYear())) {
            year = givenDate.getFullYear()
          } else {
            year = '--'
          }
          return `${month}/${day}/${year}`
        }
      } else {
        return '--/--/----'
      }
    },
    formatNumber(number) {
      // Round the number up using Math.ceil to remove decimals
      const roundedNumber = Math.ceil(number)

      // Convert the number to a string and format it with commas
      return roundedNumber.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    },
    onImageError(event) {
      event.target.src = this.logoPlaceholder
    },
    async rewriteContent(instructions) {
      this.loading = true
      this.panelOpen = false
      try {
        const res = await Comms.api.rewriteReport({
          content: this.summary,
          instructions: instructions,
          clips: this.preppedClips,
        })
        this.summary = res.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
          .replace(/^### (.*$)/gim, '<h3>$1</h3>')
          // Convert #### to <h4></h4>
          .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
          // Convert ## to <h2></h2> (if needed)
          .replace(/^## (.*$)/gim, '<h2>$1</h2>')
          // Convert # to <h1></h1> (if needed)
          .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        this.showingReportEdit = false
        this.loading = false
        this.$toast('Report updated', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        this.reportInstructions = ''
      } catch (e) {
        console.error(e)
        this.loadingText = 'Analyzing articles...'
        this.loading = false
        this.urlsSet = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getReportClips() {
      this.loadingText = 'Step 1/4: Analyzing articles...'
      this.loading = true
      this.scrollToChatTop()
      try {
        const res = await Comms.api.getReportClips({
          urls: this.urls,
        })
        this.clips = res
        this.getTrafficData()
      } catch (e) {
        console.error(e)
        this.loadingText = 'Analyzing articles...'
        this.loading = false
        this.urlsSet = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getTrafficData() {
      this.loadingText = 'Step 2/4: Gathering traffic...'
      try {
        const res = await Comms.api.getTrafficData({
          urls: this.urls,
        })
        this.traffic = res
        this.getSocialData()
      } catch (e) {
        console.error(e)
        this.loading = false
        this.urlsSet = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getSocialData() {
      this.loadingText = 'Step 3/4: Summarizing data...'
      try {
        const res = await Comms.api.getSocialData({
          urls: this.urls,
        })
        this.socialData = res
        console.log(res)
        this.combineArticlesWithTraffic()
      } catch (e) {
        console.error(e)
        this.loading = false
        this.urlsSet = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    async getReportSummary() {
      this.loadingText = 'Step 4/4: Generating report...'
      let clips = this.prepareClips(this.clips)
      this.preppedClips = clips

      try {
        const res = await Comms.api.getReportSummary({
          clips: clips,
          brand: this.brand,
        })
        this.summary = res.summary
          .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>')
          .replace(/^### (.*$)/gim, '<h3>$1</h3>')
          // Convert #### to <h4></h4>
          .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
          // Convert ## to <h2></h2> (if needed)
          .replace(/^## (.*$)/gim, '<h2>$1</h2>')
          // Convert # to <h1></h1> (if needed)
          .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        this.loading = false
        this.creating = false
      } catch (e) {
        console.error(e)
        this.urlsSet = false
        this.loading = false
        this.$toast('Error uploading clips, try again', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    prepareClips(clips) {
      console.log('SOCIAL DATA --- > : ', this.socialData)
      return clips.map(
        (a) =>
          `Description:${a.description ? a.description : ''} Date:${a.date}, Source:${
            a.source
          }, Author/s :${a.author ? a.author[0] : 'Unknown'}, Unique visitors: ${
            a.traffic ? a.traffic.users : 0
          },  Social Media engagement / shares: ${
            this.socialData[a.url] && this.socialData[a.url][0]
              ? `Facebook: ${this.socialData[a.url][0]['total_facebook_shares']}, Reddit: ${
                  this.socialData[a.url][0]['total_reddit_engagements']
                }, Pinterest: ${this.socialData[a.url][0]['pinterest_shares']}, X/Twitter: ${
                  this.socialData[a.url][0]['twitter_shares']
                } `
              : 'none'
          } `,
      )
    },
    // combineArticlesWithTraffic() {
    //   this.clips = this.clips.map((article) => {
    //     const domain = article.source.replace(/^https?:\/\//, '').replace(/^www\./, '')
    //     const traffic = this.traffic[domain] || null
    //     return {
    //       ...article,
    //       traffic,
    //     }
    //   })
    //   this.totalVisits = this.calculateTotalVisits()
    //   this.socialTotals = this.getSocialTotals()
    //   this.clipChartData = this.processClips(this.clips)
    //   this.getReportSummary()
    // },
    combineArticlesWithTraffic() {
      this.clips = this.clips.map((article) => {
        const domain = article.source.replace(/^https?:\/\//, '').replace(/^www\./, '')
        const traffic = this.traffic[domain] || null
        return {
          ...article,
          traffic,
        }
      })

      this.clips = this.clips.sort((a, b) => {
        const trafficA = a.traffic ? a.traffic.users : 0 // if no traffic, set to 0
        const trafficB = b.traffic ? b.traffic.users : 0 // if no traffic, set to 0
        return trafficB - trafficA // sort in descending order
      })

      this.totalVisits = this.calculateTotalVisits()
      this.socialTotals = this.getSocialTotals()
      this.clipChartData = this.processClips(this.clips)
      this.getReportSummary()
    },
    processClips(clips) {
      const dateMap = new Map()

      clips.forEach((clip) => {
        const date = clip.date ? new Date(clip.date).toLocaleDateString() : null
        if (date && clip.traffic && clip.traffic.users) {
          if (dateMap.has(date)) {
            const existingData = dateMap.get(date)
            dateMap.set(date, {
              clipCount: existingData.clipCount + 1,
              totalUsers: existingData.totalUsers + Number(clip.traffic.users),
            })
          } else {
            dateMap.set(date, {
              clipCount: 1,
              totalUsers: Number(clip.traffic.users),
            })
          }
        }
      })

      const sortedDates = Array.from(dateMap.keys()).sort((a, b) => {
        return new Date(a) - new Date(b)
      })

      const dateList = []
      const clipCountList = []
      const usersList = []

      sortedDates.forEach((date) => {
        const data = dateMap.get(date)
        dateList.push(date)
        clipCountList.push(data.clipCount)
        usersList.push(data.totalUsers)
      })

      return {
        dateList,
        clipCountList,
        usersList,
      }
    },
    calculateTotalVisits() {
      let totalVisits = 0
      for (let key in this.traffic) {
        if (this.traffic[key].users) {
          totalVisits += parseInt(this.traffic[key].users)
        }
      }
      return totalVisits
    },
    // getSocialTotals() {
    //   let totalFacebookLikes = 0
    //   let totalRedditLikes = 0
    //   let totalPinterestLikes = 0
    //   let totalTwitterLikes = 0

    //   for (const url in this.socialData) {
    //     if (this.socialData.hasOwnProperty(url)) {
    //       const data = this.socialData[url]

    //       if (data[0] && data[0].total_facebook_shares) {
    //         totalFacebookLikes += data[0].total_facebook_shares
    //       }

    //       if (data[0] && data[0].total_reddit_engagements) {
    //         totalRedditLikes += data[0].total_reddit_engagements
    //       }

    //       if (data[0] && data[0].twitter_shares) {
    //         totalTwitterLikes += data[0].twitter_shares
    //       }

    //       if (data[0] && data[0].pinterest_shares) {
    //         totalPinterestLikes += data[0].pinterest_shares
    //       }
    //     }
    //   }

    //   return {
    //     totalFacebookLikes,
    //     totalRedditLikes,
    //     totalPinterestLikes,
    //     totalTwitterLikes,
    //   }
    // },
    getSocialTotals() {
      let totalFacebookLikes = 0
      let totalRedditLikes = 0
      let totalPinterestLikes = 0
      let totalTwitterLikes = 0

      // Create an array to store articles along with their total social shares
      const articlesWithSocialTotals = this.clips.map((article) => {
        const socialData = this.socialData[article.url] || null
        let totalShares = 0

        if (socialData && socialData[0]) {
          const {
            total_facebook_shares,
            total_reddit_engagements,
            twitter_shares,
            pinterest_shares,
          } = socialData[0]
          totalShares += total_facebook_shares || 0
          totalShares += total_reddit_engagements || 0
          totalShares += twitter_shares || 0
          totalShares += pinterest_shares || 0

          // Accumulate totals for each platform (existing logic)
          totalFacebookLikes += total_facebook_shares || 0
          totalRedditLikes += total_reddit_engagements || 0
          totalTwitterLikes += twitter_shares || 0
          totalPinterestLikes += pinterest_shares || 0
        }

        // Return the article with its total social shares
        return {
          ...article,
          totalShares,
        }
      })

      // Sort the articles by their total social shares (from most to least)
      this.starredArticles = articlesWithSocialTotals
        .sort((a, b) => b.totalShares - a.totalShares)
        .slice(0, 3)

      // Return the totals for each platform
      return {
        totalFacebookLikes,
        totalRedditLikes,
        totalPinterestLikes,
        totalTwitterLikes,
      }
    },

    async runReport() {
      this.loading = true
      try {
        const res = await Comms.api.runReport({
          urls: this.urls,
          name: this.brand,
        })
        console.log(res)
        this.loading = false
      } catch (e) {
        console.error(e)
        this.loading = false
      } finally {
      }
    },
    handleInput() {
      const result = this.processUrls(this.reportUrls)
      this.urls = result.urls
      this.urlCount = result.count
    },
    processUrls(inputText) {
      const lines = inputText
        .split(/[\n,]+/)
        .map((line) => line.trim())
        .filter((line) => line !== '')
      const urls = []
      let count = 0

      const validTLDs = new Set([
        'com',
        'org',
        'net',
        'int',
        'edu',
        'gov',
        'mil',
        'co',
        'io',
        'me',
        'biz',
        'info',
        'xyz',
        'online',
        'site',
        'club',
        'shop',
        'blog',
        'web',
        'art',
        'app',
        'dev',
        'tech',
        'store',
        'ai',
        'us',
        'uk',
      ])

      function levenshteinDistance(a, b) {
        const matrix = []
        let i
        for (i = 0; i <= b.length; i++) {
          matrix[i] = [i]
        }
        let j
        for (j = 0; j <= a.length; j++) {
          matrix[0][j] = j
        }
        for (i = 1; i <= b.length; i++) {
          for (j = 1; j <= a.length; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
              matrix[i][j] = matrix[i - 1][j - 1]
            } else {
              matrix[i][j] = Math.min(
                matrix[i - 1][j - 1] + 1,
                matrix[i][j - 1] + 1,
                matrix[i - 1][j] + 1,
              )
            }
          }
        }
        return matrix[b.length][a.length]
      }

      function findClosestTLD(tld) {
        let minDistance = Infinity
        let closestTLD = null
        for (let validTLD of validTLDs) {
          const distance = levenshteinDistance(tld, validTLD)
          if (distance < minDistance) {
            minDistance = distance
            closestTLD = validTLD
          }
        }
        return minDistance === 1 ? closestTLD : null
      }

      for (let line of lines) {
        line = line.trim()
        if (line === '') continue

        const tldMatch = line.match(/\.([a-zA-Z]{2,})$/)
        if (tldMatch) {
          const tld = tldMatch[1].toLowerCase()
          if (!validTLDs.has(tld)) {
            const correctedTLD = findClosestTLD(tld)
            if (correctedTLD) {
              line = line.slice(0, -tld.length) + correctedTLD
            }
          }
        }
        urls.push(line)
        count++
      }

      return { urls, count }
    },

    changeView(txt) {
      this.view = txt
      if (txt === 'starred') {
        this.scrollToTopDivider()
      }
    },
    setUrls() {
      this.urlsSet = true
      this.scrollToChatTop()
    },
    uploadImage(event) {
      const file = event.target.files[0]
      this.mainImage = file

      if (!file) {
        this.fileName = ''
        alert('No file selected.')
        return
      }

      if (!this.allowedFormats.includes(file.type)) {
        alert('Only JPEG, PNG, and SVG files are allowed.')
        this.fileName = ''
        return
      }

      if (file.size > this.maxSize) {
        alert('File size should not exceed 2MB.')
        this.fileName = ''
        return
      }

      this.loading = true
      this.fileName = file.name
      this.scrollToChatTop()

      const reader = new FileReader()

      reader.onload = (e) => {
        const imageDataUrl = e.target.result
        this.uploadedImageUrl = imageDataUrl
        this.loading = false
      }

      reader.onerror = () => {
        alert('Error reading file.')
        this.fileName = ''
        this.loading = false
      }

      reader.readAsDataURL(file)
    },
    generateReportSearch() {
      if (!this.reportName) {
        this.reportName = this.searchText
        this.searchText = ''
        this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        this.scrollToChatTop()
        return
      } else if (!this.brand) {
        this.brand = this.searchText
        this.searchText = ''
        this.$refs.textarea.dispatchEvent(new Event('textarea-clear'))
        this.scrollToChatTop()
        return
      }
    },
    scrollToChatTop() {
      this.$nextTick(() => {
        const chatWindow = this.$refs.chatWindow
        chatWindow.scrollTop = chatWindow.scrollHeight
      })
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
        el.addEventListener('textarea-clear', function () {
          el.value = ''
          el.style.height = 'auto'
        })

        adjustTextareaHeight()
      },
    },

    typed: {
      bind(el, binding) {
        let text = binding.value
        let index = 0
        el.innerHTML = ''

        function type() {
          if (index < text.length) {
            el.innerHTML += text.charAt(index)
            index++
            setTimeout(type, 12)
          }
        }

        type()
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.turq-bg {
  background-color: $lite-blue !important;
}

.lite-bg {
  background-color: $lite-blue !important;
  img {
    filter: invert(100%) !important;
  }
}

.img-container-stay-alt {
  padding: 3px 5px 3px 7px;
  border-radius: 50%;
  background-color: $soft-gray;

  img {
    margin: 0;
    padding: 0;
  }
}

.opaque {
  opacity: 0.3 !important;
  cursor: text;
}

.floating-panel {
  position: absolute;
  right: 15vw;
  bottom: 10vh;
  box-shadow: 1px 3px 6px rgba(0, 0, 0, 0.2);
  border-radius: 100%;
  padding: 8px 10px;
  background: transparent;
  z-index: 100;
  cursor: pointer;
}

.expanded {
  border-radius: 20px !important;

  img {
    margin: 10px 0;
  }
}

.panel-options {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  img {
    filter: invert(40%);
  }
}

.s-tooltip-right {
  visibility: hidden;
  width: 120px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  top: 100%;
  left: 115%;
  margin-top: -30px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-tooltip-left {
  visibility: hidden;
  width: 120px;
  background-color: $graper;
  color: white;
  text-align: center;
  border-radius: 4px;
  padding: 6px 2px;
  position: absolute;
  z-index: 100;
  top: 100%;
  right: 120%;
  margin-top: -36px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-size: 13px;
  line-height: 1.4;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}

.s-wrapper {
  position: relative;
  display: inline-block;
}

.s-wrapper:hover .s-tooltip-left,
.s-wrapper:hover .s-tooltip-right {
  visibility: visible;
  opacity: 1;
}

a {
  text-decoration: none;
  color: $dark-black-blue;
}

.img-container-stay-small-txt {
  cursor: pointer;
  font-family: $base-font-family;
  color: $dark-black-blue;
  padding: 4px 8px !important;
  border-radius: 9px;
  background-color: $silver;
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 14px;

  img {
    filter: invert(20%);
    margin: 0 0 0 8px;
    padding: 0;
  }
}

.input-container-small {
  border: 1px solid rgba(0, 0, 0, 0.185);
  transition: box-shadow 0.3s ease;
  padding: 2px 0;
  border-radius: 9px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;
  background-color: white;
  margin-top: 16px;

  img {
    filter: invert(40%);
  }

  input {
    background: transparent;
    padding-left: 16px !important;
    font-family: $thin-font-family;
    width: 100%;
  }
}

.abs-img-left {
  position: absolute;
  top: 30%;
  left: -32px;
}

.abs-top-right {
  position: absolute;
  top: 12px;
  right: 12px;
}

.abs-top {
  position: absolute;
  bottom: 110%;
  right: 0;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 10px 16px;
  width: 400px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 1px 3px 6px rgba(0, 0, 0, 0.2);
  cursor: text;
}

.elipsis-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

.gold-filter {
  filter: invert(74%) sepia(68%) saturate(1511%) hue-rotate(358deg) brightness(95%) contrast(106%);
}

.blue-filter {
  filter: invert(50%) sepia(6%) saturate(4941%) hue-rotate(159deg) brightness(100%) contrast(87%);
}

.fadein {
  transition: opacity 1s ease-out;
  opacity: 0;
  animation: fadeIn 1s forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.bottom-border {
  border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  padding-bottom: 12px;
}

.pill {
  display: flex;
  flex-direction: row;
  align-items: center;
  background-color: $soft-gray;
  border-radius: 16px;
  padding: 3px 10px;
  margin-right: 8px;

  img {
    margin-right: 4px;
  }
  p {
    margin: 0 !important;
    font-size: 14px;
  }
}

.article {
  padding: 16px;
}

.article-body {
  margin-bottom: 12px;
  margin-right: 32px;
  width: 100%;
  max-height: 150px;
  overflow: hidden;

  h3 {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .report-body {
    height: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.report-body {
  font-family: $thin-font-family;
  line-height: 1.5;
  font-size: 14px;
}

.no-letter-margin {
  p {
    margin: 0 !important;
  }
}

.img-mar {
  img {
    margin-right: 4px;
  }
}

.small-text {
  font-size: 13px;
}

.medium-txt {
  font-size: 18px;
}

.bottom-margin {
  margin-bottom: 24px;
}

.bottom-margin-m {
  margin-bottom: 12px;
}

.container {
  background-color: white;
  padding: 16px;
  border-radius: 9px;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
  font-family: $thin-font-family;
  p {
    margin: 8px 0;
  }

  small {
    color: $base-gray;
  }

  &__top {
    border-bottom: 2px solid rgba(0, 0, 0, 0.05);
  }
}

.col {
  display: flex;
  flex-direction: column;
}

.active {
  background-color: $soft-gray;
}

.pre-text {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
  outline: none;
}

.pre-text:focus {
  outline: 2px solid $lite-blue;
}

::v-deep ::selection {
  background-color: $lite-blue !important;
  color: white;
}

::v-deep .pre-text {
  a {
    color: $grape;
    border-bottom: 1px solid $grape;
    font-family: $base-font-family;
    text-decoration: none;
    padding-bottom: 2px;

    &:hover {
      opacity: 0.7;
    }
  }

  strong,
  h1,
  h2,
  h3,
  h4 {
    font-family: $base-font-family;
    margin: 0;
  }

  ul {
    display: block;
    list-style-type: disc;
    margin-block-start: 0;
    margin-block-end: 0;
    margin-inline-start: 0px;
    margin-inline-end: 0px;
    padding-inline-start: 16px;
    unicode-bidi: isolate;
  }

  li {
    // margin-top: -32px;
    padding: 0;
  }
}

.photo-header-alt {
  height: 150px;
  width: 150px;
  margin: 0;
  object-fit: cover;
  border-radius: 4px;
}

.space-between-bottom {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-end;
  width: 100%;
}

.photo-header {
  height: 250px;
  width: 100%;
  margin: 0;
  object-fit: cover;
  border-radius: 5px;
}

.photo-header-small {
  height: 250px;
  width: 100%;
  margin: 0;
  object-fit: cover;
  border-radius: 5px;
}

.left-nav {
  width: 60px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background-color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  // box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);

  .nav-links {
    list-style: none;
    padding: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    .nav-item {
      margin: 10px 0;
      display: flex;
      justify-content: center;
      cursor: pointer;

      div {
        padding: 9px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        transition: background 0.3s ease;
        &:hover {
          background-color: $soft-gray;
        }

        img {
          margin: 0;
        }
      }
    }
  }
}

.thin-font {
  font-family: $thin-font-family !important;
}

.bold-font {
  font-family: $base-font-family !important;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  border-radius: 16px;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.flex-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotation {
  animation: rotation 2s infinite linear;
}

.file-input-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-family: $thin-font-family;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.file-input {
  display: none;
}

.large-input-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.025);
  border-radius: 28px;
  background-color: white;
  width: 100%;
  margin-bottom: 8px;

  @media only screen and (max-width: 600px) {
    width: 94vw !important;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 70vw !important;
  }
}

.input-container-gray {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
  padding: 18px 0 14px 0;
  border-radius: 24px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  flex-direction: column;
  background-color: white;

  section {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex-direction: row;
  }

  img {
    filter: invert(40%);
  }
}

.area-input {
  width: 100%;
  margin-bottom: 0.25rem;
  max-height: 120px !important;
  padding: 0 1.25rem;
  line-height: 1.25;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  background-color: transparent;
}
.area-input::-webkit-scrollbar {
  width: 4px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.area-input::-webkit-scrollbar-track {
  margin-top: 24px;
}

.text-area-input {
  padding-top: 1rem;
}

input,
textarea {
  font-family: $thin-font-family;
}

input::placeholder {
  font-family: $thin-font-family;
}
input:disabled {
  cursor: not-allowed;
}
textarea:disabled {
  cursor: not-allowed;
}
textarea::placeholder {
  font-family: $thin-font-family;
}

.big-chat-bubble {
  width: fit-content;
  border-radius: 12px;
  padding: 8px 16px;
  margin: 12px 0;
  background-color: white;
  box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);
}

.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.row-even {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  width: 50%;
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.rows {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 4px 0;

  div {
    width: 40%;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
    // padding-left: 12px;

    img {
      margin-right: 8px;
    }
  }
}

.reports {
  height: 100vh;
  width: 100vw;
  padding: 32px 18vw;
}
.chat-window {
  height: 96vh;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: space-evenly;
  padding: 0 5vw;

  &__header {
    width: 100%;
    position: sticky;
    top: 0;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    padding: 48px 0 12px 0;
    p {
      font-family: $base-font-family;
      font-size: 18px !important;
    }
  }

  &__body {
    height: 100%;
    width: 100%;
    overflow-y: scroll;
    padding: 0 4px;
  }

  &__footer {
    position: sticky;
    bottom: 0;
    width: 100%;
    padding: 24px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    // border-top: 1px solid rgba(0, 0, 0, 0.1);
  }

  &__chat-bubble {
    line-height: 1.5;
    width: fit-content;
    border-radius: 20px;
    padding: 8px 16px;
    margin: 12px 0;
    background-color: white;
    box-shadow: 1px 2px 6px rgba(0, 0, 0, 0.05);

    img {
      margin-right: 6px;
    }

    p {
      margin: 0;
    }
  }
}

.cursor {
  cursor: pointer;
}
.text {
  cursor: text;
  outline: 2px solid $lite-blue;
}
</style>
