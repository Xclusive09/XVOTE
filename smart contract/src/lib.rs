use anchor_lang::prelude::*;

declare_id!("YourProgramPublicKey");

#[program]
pub mod voting_system {
    use super::*;

    pub fn create_poll(ctx: Context<CreatePoll>, title: String, options: Vec<String>) -> Result<()> {
        // Your create poll logic
    }

    pub fn vote(ctx: Context<Vote>, option_index: u8) -> Result<()> {
        // Your voting logic
    }

    pub fn tally_votes(ctx: Context<TallyVotes>) -> Result<()> {
        // Your vote tallying logic
    }
}

#[account]
pub struct Poll {
    pub title: String,
    pub options: Vec<String>,
    pub votes: Vec<u64>,
    pub admin: Pubkey,
    pub end_time: i64,
}

#[account]
pub struct Voter {
    pub has_voted: bool,
    pub nft_owned: bool,
}

#[derive(Accounts)]
pub struct CreatePoll<'info> {
    #[account(init)]
    pub poll: ProgramAccount<'info, Poll>,
    pub admin: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Vote<'info> {
    #[account(mut)]
    pub poll: ProgramAccount<'info, Poll>,
    #[account(mut)]
    pub voter: ProgramAccount<'info, Voter>,
    pub signer: Signer<'info>,
}

#[derive(Accounts)]
pub struct TallyVotes<'info> {
    pub poll: ProgramAccount<'info, Poll>,
}
