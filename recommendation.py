from database import convert_bytearray_to_string
from utils import determine_meeting_status
import logging

def hybrid_recommendation(user_uuid, model, meeting_category_list_df, user_profiles, now, meeting_df):
    try:
        # UUID conversion
        logging.info("Start Hybrid Recommendation")
        user_profiles['user_uuid'] = user_profiles['user_uuid'].apply(
            lambda x: convert_bytearray_to_string(x) if isinstance(x, bytearray) else x
        )
        user_profiles_grouped = user_profiles.groupby('user_uuid')['user_category_id'].apply(list).reset_index()

        # Filter only rows with enable column equal to 1
        enabled_meetings = meeting_category_list_df[meeting_category_list_df['enable'] == 1]

        scores = []
        for _, meeting in enabled_meetings.iterrows():
            meeting_id = meeting['meeting_id']
            category_id = meeting['sub_category_id']
            meeting_status = determine_meeting_status(meeting_id, meeting_df, now)

            if meeting_status in ["모집중", "모집완료"]:
                user_categories = \
                    user_profiles_grouped[user_profiles_grouped['user_uuid'] == user_uuid]['user_category_id'].iloc[0]
                cbf_score = 1.0 if category_id in user_categories else 0.0
                cf_score = model.predict(user_uuid, meeting_id).est
                hybrid_score = (cbf_score + cf_score) / 2
                scores.append((meeting_id, hybrid_score))

        top_3_meetings = sorted(scores, key=lambda x: x[1], reverse=True)[:3]
        logging.info("Hybrid recommendation complete")
        return [meeting_id for meeting_id, _ in top_3_meetings]

    except (KeyError, ValueError) as e:
        logging.error(f"Error during recommendation: {str(e)}")
        raise ValueError(f"This user does not exist.")